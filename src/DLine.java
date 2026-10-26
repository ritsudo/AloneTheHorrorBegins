/** One spoken line: a portrait id, the speaker label and the text. */
class DLine {
    int portrait;
    String speaker;
    String text;

    DLine(int portrait, String speaker, String text) {
        this.portrait = portrait;
        this.speaker = speaker;
        this.text = text;
    }
}
