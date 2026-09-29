#include "managed_font.h"

#include <bitset>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <vector>

struct FakeFontInfo {
	uint8_t pointSize{};
	uint8_t width{};
	uint8_t height{};
	uint8_t ascent{};
	uint8_t inleading{};
	uint8_t exleading{};
	uint8_t flags{};
	uint16_t weight{};
	uint16_t charset{};
	const uint8_t *data{};
	const uint32_t *chptr{};
	uint16_t codepage{};
};

class FakeBuffer {
	public:
		explicit FakeBuffer(std::size_t size) : bytes_(size) {}
		uint8_t *getBuffer() { return bytes_.data(); }
		const uint8_t *getBuffer() const { return bytes_.data(); }
		std::size_t size() const { return bytes_.size(); }
	private:
		std::vector<uint8_t> bytes_;
};

using Font = ManagedFont<FakeFontInfo, FakeBuffer>;

static void putOffset(FakeBuffer &buffer, std::size_t index, uint32_t offset) {
	std::memcpy(buffer.getBuffer() + index * sizeof(offset), &offset, sizeof(offset));
}

static int capture(std::shared_ptr<Font> const &font, const uint8_t *screen) {
	std::bitset<256> candidates;
	candidates.set();
	const std::size_t bytes = Font::glyphBytes(font->info.width, font->info.height);
	for (std::size_t byte = 0; byte < bytes; ++byte) {
		for (std::size_t character = 0; character < 256; ++character) {
			if (candidates[character] && font->glyph(static_cast<uint8_t>(character))[byte] != screen[byte]) {
				candidates.reset(character);
			}
		}
	}
	for (unsigned index = 32; index <= 255 + 31; ++index) {
		const uint8_t character = static_cast<uint8_t>(index);
		if (candidates[character]) return character;
	}
	return 0;
}

int main() {
	unsigned checks = 0;

	// Maximum command dimensions remain size_t-exact rather than wrapping at 8 bits.
	static_assert(Font::glyphBytes(255, 255) == 8160);
	static_assert(Font::fontBytes(255, 255) == 2088960);
	auto maximumData = std::make_shared<FakeBuffer>(Font::fontBytes(255, 255));
	auto maximum = std::make_shared<Font>(maximumData, 255, 255, 254, 0);
	assert(maximum->geometryFits(255, 255));
	assert(maximum->glyph(255) + Font::glyphBytes(255, 255) ==
		maximumData->getBuffer() + maximumData->size());
	checks += 2;

	// Short data and unsafe mutations fail without altering the selected geometry.
	auto data = std::make_shared<FakeBuffer>(Font::fontBytes(8, 8));
	auto font = std::make_shared<Font>(data, 8, 8, 7, 0);
	assert(font->geometryFits(8, 8));
	assert(!font->geometryFits(9, 8));
	assert(!font->setWidth(9) && font->info.width == 8);
	assert(!font->setHeight(9) && font->info.height == 8);
	assert(!font->setWidth(0) && !font->setHeight(0));
	checks += 5;

	// Offset metadata must contain all 256 entries and every referenced glyph.
	auto shortOffsets = std::make_shared<FakeBuffer>(Font::characterPointerBytes - 1);
	assert(!font->setCharacterPointers(shortOffsets));
	auto offsets = std::make_shared<FakeBuffer>(Font::characterPointerBytes);
	for (std::size_t index = 0; index < 256; ++index) putOffset(*offsets, index, 0);
	putOffset(*offsets, 255, static_cast<uint32_t>(data->size() - 7));
	assert(!font->setCharacterPointers(offsets));
	putOffset(*offsets, 255, static_cast<uint32_t>(data->size() - 8));
	assert(font->setCharacterPointers(offsets));
	assert(font->info.chptr == nullptr); // Reserved metadata does not alter rendering.
	checks += 4;

	// Destroying buffer-table entries cannot destroy storage retained by the font.
	std::weak_ptr<FakeBuffer> dataLifetime = data;
	std::weak_ptr<FakeBuffer> offsetLifetime = offsets;
	data.reset();
	offsets.reset();
	shortOffsets.reset();
	assert(!dataLifetime.expired() && !offsetLifetime.expired());
	font->dataOwner()->getBuffer()[255 * 8 + 7] = 0xA5;
	assert(font->glyph(255)[7] == 0xA5);
	checks += 2;

	// The fixed-size candidate capture preserves the official 32..255,0..31 priority.
	for (std::size_t character = 0; character < 256; ++character) {
		for (std::size_t byte = 0; byte < 8; ++byte) {
			font->dataOwner()->getBuffer()[character * 8 + byte] =
				static_cast<uint8_t>(character * 17 + byte * 29);
		}
	}
	assert(capture(font, font->glyph('A')) == 'A');
	std::memcpy(font->dataOwner()->getBuffer(), font->glyph(' '), 8);
	assert(capture(font, font->glyph(0)) == ' ');
	checks += 2;

	// An attached table is revalidated when geometry changes, before mutation.
	auto roomyData = std::make_shared<FakeBuffer>(4096);
	auto roomy = std::make_shared<Font>(roomyData, 8, 8, 7, 0);
	auto edgeOffsets = std::make_shared<FakeBuffer>(Font::characterPointerBytes);
	for (std::size_t index = 0; index < 256; ++index) putOffset(*edgeOffsets, index, 4088);
	assert(roomy->setCharacterPointers(edgeOffsets));
	assert(!roomy->setWidth(9) && roomy->info.width == 8);
	checks += 2;

	std::cout << checks << " font safety checks passed\n";
}
