#define _GNU_SOURCE
#include <SDL3/SDL.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Feed only this headless SDL process; production app and VDP are unchanged. */
bool SDL_PollEvent(SDL_Event *event) {
    static bool (*real_poll)(SDL_Event *);
    static int fd = -1;
    static SDL_Scancode held;
    static Uint64 release_at;
    if (!real_poll) real_poll = dlsym(RTLD_NEXT, "SDL_PollEvent");
    if (fd < 0) fd = open(getenv("SHAPES_REVIEW_KEYS"), O_RDONLY | O_NONBLOCK);
    if (event && held && SDL_GetTicks() >= release_at) {
        memset(event, 0, sizeof(*event));
        event->type = SDL_EVENT_KEY_UP;
        event->key.scancode = held;
        held = 0;
        return true;
    }
    char key;
    if (event && !held && read(fd, &key, 1) == 1) {
        SDL_Scancode scan = SDL_SCANCODE_SPACE;
        SDL_Keycode code = SDLK_SPACE;
        if (key == 27) { scan = SDL_SCANCODE_ESCAPE; code = SDLK_ESCAPE; }
        else if (key == '\n') { scan = SDL_SCANCODE_RETURN; code = SDLK_RETURN; }
        else if (key == '.') { scan = SDL_SCANCODE_PERIOD; code = SDLK_PERIOD; }
        else if (key >= 'a' && key <= 'z') { scan = SDL_SCANCODE_A + key - 'a'; code = key; }
        else if (key >= '1' && key <= '9') { scan = SDL_SCANCODE_1 + key - '1'; code = key; }
        else if (key == '0') { scan = SDL_SCANCODE_0; code = SDLK_0; }
        memset(event, 0, sizeof(*event));
        event->type = SDL_EVENT_KEY_DOWN;
        event->key.scancode = held = scan;
        event->key.key = code;
        event->key.down = true;
        release_at = SDL_GetTicks() + 150;
        return true;
    }
    return real_poll(event);
}

/* Capture the real rendered frame on request; no drawing is synthesized. */
bool SDL_RenderPresent(SDL_Renderer *renderer) {
    static bool (*real_present)(SDL_Renderer *);
    if (!real_present) real_present = dlsym(RTLD_NEXT, "SDL_RenderPresent");
    const char *request = getenv("SHAPES_REVIEW_CAPTURE");
    if (request) {
        FILE *file = fopen(request, "r");
        if (file) {
            char target[4096];
            if (fgets(target, sizeof(target), file)) {
                target[strcspn(target, "\r\n")] = 0;
                int width, height;
                SDL_GetRenderOutputSize(renderer, &width, &height);
                /* Fab --scale integer centres an integer multiple of mode 20.
                 * A desktop window can be much larger than the headless one. */
                int scale = width / 512 < height / 384 ? width / 512 : height / 384;
                if (scale < 1) scale = 1;
                SDL_Rect area = {(width-512*scale)/2, (height-384*scale)/2,
                                 512*scale, 384*scale};
                SDL_Surface *surface = SDL_RenderReadPixels(renderer, &area);
                if (surface) { SDL_SaveBMP(surface, target); SDL_DestroySurface(surface); }
            }
            fclose(file);
            unlink(request);
        }
    }
    return real_present(renderer);
}

/* Label the review window without changing either test image. */
SDL_Window *SDL_CreateWindow(const char *title, int w, int h, SDL_WindowFlags flags) {
    static SDL_Window *(*real_create)(const char *, int, int, SDL_WindowFlags);
    if (!real_create) real_create = dlsym(RTLD_NEXT, "SDL_CreateWindow");
    const char *label = getenv("PAIRED_REVIEW_TITLE");
    /* Exercise a scaled window with SDL's dummy driver before human review. */
    const char *size_test = getenv("PAIRED_REVIEW_WINDOW_SCALE");
    if (size_test && atoi(size_test) == 3) { w = 1536; h = 1152; }
    return real_create(label ? label : title, w, h, flags);
}
