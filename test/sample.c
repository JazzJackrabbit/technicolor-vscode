/* A projection booth scheduler for a silent-film cinema. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_REELS 12
#define FRAME_RATE 16 /* silent-era projection speed, frames per second */
#define LEADER_SECONDS 8

enum genre {
    GENRE_COMEDY,
    GENRE_MELODRAMA,
    GENRE_SERIAL,
    GENRE_NEWSREEL,
};

static const char *genre_names[] = {
    [GENRE_COMEDY] = "comedy",
    [GENRE_MELODRAMA] = "melodrama",
    [GENRE_SERIAL] = "serial",
    [GENRE_NEWSREEL] = "newsreel",
};

struct reel {
    char title[64];
    unsigned year;
    enum genre genre;
    unsigned long frames;
    int tinted; /* nitrate prints were often tinted by scene */
};

struct programme {
    struct reel reels[MAX_REELS];
    size_t count;
    time_t curtain;
};

/* Running time of a reel in whole seconds at silent speed. */
static unsigned long reel_seconds(const struct reel *r)
{
    return r->frames / FRAME_RATE + LEADER_SECONDS;
}

static int programme_add(struct programme *p, const char *title,
                         unsigned year, enum genre g, unsigned long frames)
{
    if (p->count >= MAX_REELS) {
        fprintf(stderr, "programme full, cannot add %s\n", title);
        return -1;
    }

    struct reel *r = &p->reels[p->count++];
    strncpy(r->title, title, sizeof(r->title) - 1);
    r->title[sizeof(r->title) - 1] = '\0';
    r->year = year;
    r->genre = g;
    r->frames = frames;
    r->tinted = (g == GENRE_MELODRAMA);
    return 0;
}

static unsigned long programme_runtime(const struct programme *p)
{
    unsigned long total = 0;
    for (size_t i = 0; i < p->count; i++)
        total += reel_seconds(&p->reels[i]);
    return total;
}

/* Sort reels so the newsreel opens and the serial closes the night. */
static int reel_order(const void *a, const void *b)
{
    const struct reel *ra = a, *rb = b;
    if (ra->genre != rb->genre)
        return (int)ra->genre - (int)rb->genre;
    return (int)ra->year - (int)rb->year;
}

static void programme_print(const struct programme *p)
{
    char stamp[32];
    strftime(stamp, sizeof(stamp), "%H:%M", localtime(&p->curtain));
    printf("curtain at %s — %zu reels\n\n", stamp, p->count);

    for (size_t i = 0; i < p->count; i++) {
        const struct reel *r = &p->reels[i];
        unsigned long secs = reel_seconds(r);
        printf("%2zu. %-28s (%u, %s)%s %2lu:%02lu\n",
               i + 1, r->title, r->year, genre_names[r->genre],
               r->tinted ? " [tinted]" : "         ",
               secs / 60, secs % 60);
    }

    unsigned long total = programme_runtime(p);
    printf("\ntotal runtime %lu:%02lu, plus intermission\n",
           total / 60, total % 60);
}

int main(void)
{
    struct programme tonight = { .curtain = time(NULL) };

    programme_add(&tonight, "Topical Budget No. 312", 1927,
                  GENRE_NEWSREEL, 14400);
    programme_add(&tonight, "The Clockmaker's Daughter", 1923,
                  GENRE_MELODRAMA, 86400);
    programme_add(&tonight, "Two Left Boots", 1925,
                  GENRE_COMEDY, 28800);
    programme_add(&tonight, "Peril of the Rails, Ch. 4", 1926,
                  GENRE_SERIAL, 19200);

    qsort(tonight.reels, tonight.count, sizeof(struct reel), reel_order);
    programme_print(&tonight);

    return EXIT_SUCCESS;
}
