import java.util.Vector;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * Draws the wooden dialogue box with a typewriter reveal. The portrait for the
 * current speaker is shown at the upper right, the name is right aligned inside
 * the name bar and the wrapped body text sits below the divider rule.
 */
class Dialogue {
    static final int PANEL_Y = 136;
    static final int NAME_RIGHT = 141;
    static final int NAME_Y = 143;
    static final int BODY_X = 15;
    static final int BODY_Y = 167;
    static final int BODY_STEP = 10;
    static final int BODY_MAX = 140;
    static final int NARR_LINES = 4;
    static final int NAMED_LINES = 3;
    static final int WRAP_SCALE = 1;

    Vector lines = new Vector();
    int idx = 0;
    String[] wrapped;
    int page = 0;
    int pages = 1;
    int shown = 0;
    int total = 0;
    boolean active = false;
    int tick = 0;

    Fnt dark;

    Dialogue() {
        dark = Fnt.get(Fnt.INK);
    }

    void start(Vector ls) {
        lines = ls;
        idx = 0;
        page = 0;
        active = ls.size() > 0;
        prepare();
    }

    private boolean isNarr(DLine l) {
        return l.portrait < 0 && (l.speaker == null || l.speaker.length() == 0);
    }

    private void prepare() {
        DLine l = (DLine) lines.elementAt(idx);
        String[] all = dark.wrap(l.text, BODY_MAX * WRAP_SCALE);
        int per = isNarr(l) ? NARR_LINES : NAMED_LINES;
        if (per < 1) {
            per = 1;
        }
        pages = (all.length + per - 1) / per;
        if (pages < 1) {
            pages = 1;
        }
        if (page >= pages) {
            page = 0;
        }
        int from = page * per;
        int to = all.length < from + per ? all.length : from + per;
        wrapped = new String[to - from];
        total = 0;
        for (int i = from; i < to; i++) {
            wrapped[i - from] = all[i];
            total += all[i].length();
        }
        shown = 0;
        tick = 0;
    }

    void update() {
        if (!active) {
            return;
        }
        tick++;
        if (tick >= 2 && shown < total) {
            tick = 0;
            shown++;
        }
    }

    /** Fire pressed. Returns true when the whole conversation is finished. */
    boolean advance() {
        if (!active) {
            return true;
        }
        if (shown < total) {
            shown = total;
            return false;
        }
        if (page < pages - 1) {
            page++;
            prepare();
            return false;
        }
        idx++;
        page = 0;
        if (idx >= lines.size()) {
            active = false;
            return true;
        }
        prepare();
        return false;
    }

    boolean isActive() {
        return active;
    }

    void paint(Graphics g) {
        if (!active) {
            return;
        }
        DLine l = (DLine) lines.elementAt(idx);
        boolean narr = isNarr(l);
        // the panel is pinned to the bottom 72 px exactly as in the demo
        // (y = 136..207, body lines at 167/177/187/197)
        int bodyY;
        if (narr) {
            drawFrame(g, PANEL_Y);
            bodyY = BODY_Y;
        } else {
            drawFrame(g, PANEL_Y);
            drawNamePlank(g);
            bodyY = BODY_Y;
        }
        if (!narr && Assets.portraits != null && l.portrait >= 0
                && Assets.portraits[l.portrait] != null
                && Assets.portraits[l.portrait][0] != null) {
            g.drawImage(Assets.portraits[l.portrait][0], 144, 120, Graphics.TOP | Graphics.LEFT);
        }
        if (!narr && l.speaker != null && l.speaker.length() > 0) {
            dark.drawRight(g, l.speaker, NAME_RIGHT, NAME_Y);
        }
        int left = shown;
        for (int i = 0; i < wrapped.length; i++) {
            String w = wrapped[i];
            int n = left >= w.length() ? w.length() : left;
            if (n < 0) {
                n = 0;
            }
            dark.draw(g, w.substring(0, n), BODY_X, bodyY + i * BODY_STEP);
            left -= w.length();
            if (left <= 0) {
                break;
            }
        }
    }

    static final int BORDER_TOP = 9;
    static final int BORDER_BOT = 2;
    static final int TILE_H = 24;
    static final int TILE_Y = 52;

    /**
     * The dialogue box is the parchment page itself: its ornate top and bottom
     * borders plus tiled slices of the interior paper, pinned to the screen
     * edge. The top rises with the number of wrapped lines.
     */
    private void drawFrame(Graphics g, int top) {
        Image p = Assets.page;
        if (p == null) {
            g.setColor(0xE6D2B0);
            g.fillRect(0, top, Game.W, 208 - top);
            return;
        }
        int bottom = 208 - BORDER_BOT;
        int y = top + BORDER_TOP;
        while (y < bottom) {
            int h = TILE_H;
            if (y + h > bottom) {
                h = bottom - y;
            }
            g.drawRegion(p, 0, TILE_Y, 176, h, Sprite.TRANS_NONE,
                    0, y, Graphics.TOP | Graphics.LEFT);
            y += h;
        }
        g.drawRegion(p, 0, 0, 176, BORDER_TOP, Sprite.TRANS_NONE,
                0, top, Graphics.TOP | Graphics.LEFT);
        g.drawRegion(p, 0, 208 - BORDER_BOT, 176, BORDER_BOT, Sprite.TRANS_NONE,
                0, bottom, Graphics.TOP | Graphics.LEFT);
    }

    /** Dark plank and divider that separate the speaker name from the body. */
    private void drawNamePlank(Graphics g) {
        g.setColor(0x35200F);
        g.fillRect(9, PANEL_Y + 20, 133, 6);
        g.setColor(0x1A0E06);
        g.fillRect(9, PANEL_Y + 24, 133, 2);
    }
}
