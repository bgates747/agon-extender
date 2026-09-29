#ifndef MANAGED_FONT_H
#define MANAGED_FONT_H

// AUDIT-010 RP03: ownership and bounds for application-defined fonts.
//
// Official VDP 2.16 supports fixed-width fonts only. The character-pointer
// property is retained as metadata for forward compatibility, but it must not
// affect rendering until variable-width fonts are supported. Keeping both
// buffers here makes every FontInfo raw pointer subordinate to shared storage.

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <utility>

template <typename FontInfo, typename Buffer>
class ManagedFont {
	public:
		FontInfo info{};

		static constexpr std::size_t characterCount = 256;
		static constexpr std::size_t characterPointerBytes =
			characterCount * sizeof(uint32_t);

		ManagedFont(std::shared_ptr<Buffer> data, uint8_t width, uint8_t height,
			uint8_t ascent, uint8_t flags) : data_(std::move(data)) {
			info.width = width;
			info.height = height;
			info.ascent = ascent;
			info.flags = flags;
			info.data = data_->getBuffer();
			info.chptr = nullptr;
		}

		static constexpr std::size_t glyphBytes(uint8_t width, uint8_t height) {
			return ((std::size_t(width) + 7) / 8) * std::size_t(height);
		}

		static constexpr std::size_t fontBytes(uint8_t width, uint8_t height) {
			return glyphBytes(width, height) * characterCount;
		}

		bool geometryFits(uint8_t width, uint8_t height) const {
			if (width == 0 || height == 0 || fontBytes(width, height) > data_->size()) {
				return false;
			}
			return offsetsFit(characterPointers_, width, height);
		}

		bool setWidth(uint8_t width) {
			if (!geometryFits(width, info.height)) {
				return false;
			}
			info.width = width;
			return true;
		}

		bool setHeight(uint8_t height) {
			if (!geometryFits(info.width, height)) {
				return false;
			}
			info.height = height;
			return true;
		}

		bool setCharacterPointers(std::shared_ptr<Buffer> pointers) {
			if (!offsetsFit(pointers, info.width, info.height)) {
				return false;
			}
			characterPointers_ = std::move(pointers);
			// Font-API.md states this reserved property does not affect rendering.
			// In particular, Canvas selects its variable-width path from chptr.
			info.chptr = nullptr;
			return true;
		}

		const uint8_t *glyph(uint8_t character) const {
			return info.data + std::size_t(character) * glyphBytes(info.width, info.height);
		}

		std::shared_ptr<Buffer> const &dataOwner() const {
			return data_;
		}

		std::shared_ptr<Buffer> const &characterPointerOwner() const {
			return characterPointers_;
		}

	private:
		bool offsetsFit(std::shared_ptr<Buffer> const &pointers, uint8_t width,
			uint8_t height) const {
			if (!pointers) {
				return true;
			}
			if (pointers->size() < characterPointerBytes) {
				return false;
			}

			const std::size_t glyphSize = glyphBytes(width, height);
			const std::size_t dataSize = data_->size();
			for (std::size_t index = 0; index < characterCount; ++index) {
				uint32_t offset = 0;
				std::memcpy(&offset,
					pointers->getBuffer() + index * sizeof(offset), sizeof(offset));
				if (offset > dataSize || glyphSize > dataSize - offset) {
					return false;
				}
			}
			return true;
		}

		std::shared_ptr<Buffer> data_;
		std::shared_ptr<Buffer> characterPointers_;
};

#endif // MANAGED_FONT_H
