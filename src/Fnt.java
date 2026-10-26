import java.util.Vector;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

/**
 * Proportional bitmap font renderer. The glyph atlases are baked at build time
 * (one PNG per tint) so no runtime pixel manipulation is needed, which keeps the
 * renderer compatible with plain MIDP 2.0 Image.
 */
class Fnt {
    static final int BODY = 0;
    static final int BIG = 1;

    static final int INK = 0x1A0A04;

    private static Vector cache = new Vector();

    Image img;
    int color;
    int kind;

    private Fnt(Image img, int color, int kind) {
        this.img = img;
        this.color = color;
        this.kind = kind;
    }

    static Fnt get(int color) {
        return get(color, BODY);
    }

    static Fnt getMenu(int color) {
        return get(color, BODY);
    }

    static Fnt getBig(int color) {
        return get(color, BIG);
    }

    static Fnt getSmall(int color) {
        return get(color, BODY);
    }

    static Fnt getLoad(int color) {
        return get(color, BIG);
    }

    private static Fnt get(int color, int kind) {
        int key = color * 8 + kind;
        for (int i = 0; i < cache.size(); i++) {
            Fnt f = (Fnt) cache.elementAt(i);
            if (f.color * 8 + f.kind == key) {
                return f;
            }
        }
        Assets.ensure();
        Image im;
        if (kind == BIG) {
            im = Assets.fontBig;
        } else if (color == 0xC03020) {
            im = Assets.fontRed;
        } else if (color == 0xD8C0A0 || color == 0xE8D8B8) {
            im = Assets.fontCream;
        } else {
            im = Assets.font;
        }
        Fnt f = new Fnt(im, color, kind);
        cache.addElement(f);
        return f;
    }

    int height() {
        return kind == BIG ? FntDataBig.H : FntData.H;
    }

    int charW(int c) {
        int[] adv = kind == BIG ? FntDataBig.ADV : FntData.ADV;
        if (c < 0 || c >= adv.length) {
            return 0;
        }
        return adv[c];
    }

    int width(String s) {
        int w = 0;
        for (int i = 0; i < s.length(); i++) {
            w += charW(s.charAt(i));
        }
        return w;
    }

    void draw(Graphics g, char c, int x, int y) {
        if (c == ' ') {
            return;
        }
        int[] gx = kind == BIG ? FntDataBig.GX : FntData.GX;
        int[] gw = kind == BIG ? FntDataBig.GW : FntData.GW;
        int h = kind == BIG ? FntDataBig.H : FntData.H;
        int i = c;
        if (i < 0 || i >= gx.length || gx[i] < 0 || gw[i] == 0) {
            return;
        }
        g.drawRegion(img, gx[i], 0, gw[i], h,
                javax.microedition.lcdui.game.Sprite.TRANS_NONE, x, y,
                Graphics.TOP | Graphics.LEFT);
    }

    void draw(Graphics g, String s, int x, int y) {
        int cx = x;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            draw(g, c, cx, y);
            cx += charW(c);
        }
    }

    void drawCenter(Graphics g, String s, int cx, int y) {
        draw(g, s, cx - width(s) / 2, y);
    }

    void drawRight(Graphics g, String s, int rx, int y) {
        draw(g, s, rx - width(s), y);
    }

    /** Wrap text into lines no wider than maxW. Returns String[]. */
    String[] wrap(String text, int maxW) {
        Vector lines = new Vector();
        String rest = text;
        while (rest.length() > 0) {
            int cut = rest.length();
            if (width(rest) > maxW) {
                cut = rest.length();
                while (cut > 0 && width(rest.substring(0, cut)) > maxW) {
                    int sp = rest.lastIndexOf(' ', cut - 1);
                    if (sp <= 0) {
                        cut = 1;
                        while (cut < rest.length() && width(rest.substring(0, cut + 1)) <= maxW) {
                            cut++;
                        }
                        break;
                    }
                    cut = sp;
                }
            }
            String line = rest.substring(0, cut).trim();
            lines.addElement(line);
            rest = rest.substring(cut).trim();
        }
        String[] out = new String[lines.size()];
        for (int i = 0; i < out.length; i++) {
            out[i] = (String) lines.elementAt(i);
        }
        return out;
    }
}
