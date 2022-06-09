# Slideshow based on https://codepen.io/rokobuljan/pen/XXzqKQ

from js import console, document, window
from pyodide import create_proxy
from pyodide.http import pyfetch

CSS_TEMPLATE = """
*{{box-sizing: border-box; -webkit-box-sizing: border-box; }}
html, body {{ height: 100%; }}
body {{
    margin: 0;
    /* font: 16px/1.3 sans-serif; */
}}

/*
PURE RESPONSIVE CSS3 SLIDESHOW GALLERY by Roko C. buljan
http://stackoverflow.com/a/34696029/383904
*/

.CSSgal {{
    position: relative;
    overflow: hidden;
    height: 100%; /* Or set a fixed height */
}}

/* SLIDER */

.CSSgal .slider {{
    height: 100%;
    white-space: nowrap;
    font-size: 0;
    transition: 0.8s;
}}

/* SLIDES */

.CSSgal .slider > * {{
    font-size: 1rem;
    display: inline-block;
    white-space: normal;
    vertical-align: top;
    height: 100%;
    width: 100%;
    background: none 50% no-repeat;
    background-size: cover;
}}

/* PREV/NEXT, CONTAINERS & ANCHORS */

.CSSgal .prevNext {{
    position: absolute;
    z-index: 1;
    top: 50%;
    width: 100%;
    height: 0;
}}

.CSSgal .prevNext > div+div {{
    visibility: hidden; /* Hide all but first P/N container */
}}

.CSSgal .prevNext a {{
    background: #fff;
    position: absolute;
    width:       60px;
    height:      60px;
    line-height: 60px; /* If you want to place numbers */
    text-align: center;
    opacity: 0.7;
    -webkit-transition: 0.3s;
                    transition: 0.3s;
    -webkit-transform: translateY(-50%);
                    transform: translateY(-50%);
    left: 0;
}}
.CSSgal .prevNext a:hover {{
    opacity: 1;
}}
.CSSgal .prevNext a+a {{
    left: auto;
    right: 0;
}}

/* NAVIGATION */

.CSSgal .bullets {{
    position: absolute;
    z-index: 2;
    bottom: 0;
    padding: 10px 0;
    width: 100%;
    text-align: center;
}}
.CSSgal .bullets > a {{
    display: inline-block;
    width:       30px;
    height:      30px;
    line-height: 30px;
    text-decoration: none;
    text-align: center;
    background: rgba(255, 255, 255, 1);
    -webkit-transition: 0.3s;
                    transition: 0.3s;
}}
.CSSgal .bullets > a+a {{
    background: rgba(255, 255, 255, 0.5); /* Dim all but first */
}}
.CSSgal .bullets > a:hover {{
    background: rgba(255, 255, 255, 0.7) !important;
}}

/* NAVIGATION BUTTONS */
/* ALL: */
.CSSgal >s:target ~ .bullets >* {{      background: rgba(255, 255, 255, 0.5);}}
/* ACTIVE */
{navi_btns}
/* More slides? Add here more rules */

/* PREV/NEXT CONTAINERS VISIBILITY */
/* ALL: */
.CSSgal >s:target ~ .prevNext >* {{      visibility: hidden;}}
/* ACTIVE: */
{prev_next_visibility}
/* More slides? Add here more rules */

/* SLIDER ANIMATION POSITIONS */
{slider_anim_pos}
/* More slides? Add here more rules */

/* NAVIGATION */

div.slide-source-btn {{
    color: darkgrey;
    position: absolute;
    z-index: 2;
    top: 0;
    padding: 10px 0;
    width: 100%;
    text-align: center;
}}

div.slide-source-btn > a {{
    display: inline-block;
    width:       50px;
    height:      50px;
    line-height: 50px;
    text-decoration: none;
    text-align: center;
    background: rgba(255, 255, 255, 1);
    -webkit-transition: 0.3s;
    transition: 0.3s;
}}
div.slide-source-btn > a+a {{
    background: rgba(255, 255, 255, 0.5); /* Dim all but first */
}}
div.slide-source-btn > a:hover {{
    background: rgba(255, 255, 255, 0.7) !important;
}}
"""

NAVIG_BTN_TEMPL = (
    "#s%i:target ~ .bullets >*:nth-child(%i) {background: rgba(255, 255, 255,   1);}"
)
PREV_NEXT_VIS_TEMPL = "#s%i:target ~ .prevNext >*:nth-child(%i) {visibility: visible;}"
SLIDER_ANIM_POS_TEMPL = (
    "#s%i:target ~ .slider {transform: translateX(   %s%%); "
    "-webkit-transform: translateX(   %s%%);}"
)


class ExtensionTemplate:
    theme = None

    @property
    def children(self):
        return self._children

    def connect(self):
        return


class SlideShow(ExtensionTemplate):
    def __init__(self, parent):
        console.log("INITIALIZING IT")

        self.parent = parent

        self.source = parent.getAttribute("src") or ""

        self._children = []
        self._id = self.parent.id
        self.slides = []

        loc = document.location
        self.base = loc.origin + loc.pathname + "#s%s"
        self.compute_index()
        # try:
        #     self.index = int(loc.hash.replace('#s', '') or 1)
        # except:
        #     self.index = 1

        console.log("INDEX", self.index)
        self.register_events()
        console.log("ALLDONE IT")

    def compute_index(self, *args, **kws):
        try:
            self.index = int(document.location.hash.replace("#s", "") or 1)
        except TypeError:
            self.index = 1

    #     self.map_show_source()

    # def map_show_source(self):
    #     show_src_btn = Element("slide-source-btn")
    #     show_src_btn.element.onclick = self.show_source

    # def show_source(self, evt):
    #     console.log("show source")
    #     el = Element("slide_source").element

    #     try:
    #         if el.style.visibility == "hidden":
    #             el.style.visibility = "visible"
    #             el.innerHTML = self.slides[self.index-1]
    #         else:
    #             el.style.visibility = "hidden"
    #             el.innerHTML = ""
    #     except IndexError:
    #         console.log("OH NO", len(self.slides), self.index)

    def register_events(self):
        console.log("registering event")
        # document.onkeypress = self.catch_event
        document.onkeydown = self.catch_arrow_event

        def loc_changed(*args, **kws):
            console.log("location changed!")
            loc = document.location
            console.log(loc.hash)

        console.log("connected locationchange...")
        # window.addEventListener('locationchange', loc_changed)
        window.addEventListener("hashchange", create_proxy(self.compute_index))
        console.log("connected locationchange...DONE!")

    def catch_arrow_event(self, evt, *args, **kws):
        console.log(evt)
        console.log(evt.keyCode)
        console.log(evt.keyCode in {"37", "40", 37, 40})
        if evt.keyCode in {"37", "40", 37, 40}:
            console.log("->")
            self.previous()
        if evt.keyCode in {"38", "39", 38, 39}:
            console.log("<-")
            self.next()

    def catch_event(self, evt, *args, **kws):
        console.log(evt)
        if evt.key in {"a", ","}:
            console.log("->")
            self.previous()
        if evt.key in {"d", "."}:
            console.log("<-")
            self.next()

    def next(self):
        console.log("next", self.index)
        if self.index >= len(self.slides):
            self.index = 1
        else:
            self.index += 1
        console.log("next-->", self.index)
        self.move_slide()

    def previous(self):
        console.log("prev", self.index)
        if self.index < 2:
            self.index = len(self.slides)
        else:
            self.index -= 1
        console.log("prev-->", self.index)
        self.move_slide()

    def move_slide(self):
        console.log("move")
        url = self.base % self.index
        console.log(url)
        document.location.href = url

    def connect(self):
        console.log("Connecting...")
        pyscript.run_until_complete(self.get_slides())

    def add_style(self, styles):
        console.log("adding style...")
        # console.log(styles)
        # Create style document
        css = document.createElement("style")
        css.type = "text/css"
        console.log("TAGA")
        css.appendChild(document.createTextNode(styles))
        console.log("TOGA")
        # Append style to the tag name
        document.getElementsByTagName("head")[0].appendChild(css)
        console.log("DONE adding style...")

    async def get_slides(self):
        console.log("GHEEET source", self.source)
        response = await pyfetch("./slides.slides")
        console.log("GOT RESP source", response)
        self._source = await response.string()
        console.log("DOINE source", self._source)

        self.slides = slides_content = self._source.split("--- new ---")
        slides_headers = []
        slides_navi = []
        cleaned_content = []
        extra_css = {
            "slider_anim_pos": [],
            "prev_next_visibility": [],
            "navi_btns": [],
        }
        console.log("--- FOOOOR ---")
        for i, content in enumerate(slides_content):
            # cur_slide = i + 1
            # percentage = i * -100
            console.log("--- FAAAOOOR ---")

            cur_slide = i + 1
            perc = i * (-100)

            extra_css["slider_anim_pos"].append(
                SLIDER_ANIM_POS_TEMPL % (cur_slide, perc, perc)
            )
            console.log("--- FOOOOR ---")
            extra_css["prev_next_visibility"].append(
                PREV_NEXT_VIS_TEMPL % (cur_slide, cur_slide)
            )
            extra_css["navi_btns"].append(NAVIG_BTN_TEMPL % (cur_slide, cur_slide))

            slides_headers.append(f'<s id="s{i+1}"></s>')
            if i == 0:
                prev = len(slides_content)
            else:
                prev = i

            if i == len(slides_content) - 1:
                next = 1
            else:
                next = i + 2
            cleaned_content.append(content)
            console.log("-------------")

            console.log(content)
            slides_navi.append(
                f'<div><a href="#s{prev}"></a><a href="#s{next}"></a></div>'
            )

        console.log("DONEO))))")
        for k, v in extra_css.items():
            console.log("----->", k)
            extra_css[k] = "\n".join(v)

        print(extra_css)
        console.log("------->JOO-----")
        new_css = CSS_TEMPLATE.format(**extra_css)
        console.log("------->IIIOO-----")
        self.add_style(new_css)

        console.log("JOO-----")
        console.log(";;;".join(slides_headers))
        console.log("J0000O-----")
        self.main_div = Element.create_("div", self._id + "-gal", "CSSgal")
        self.slides_wrap = Element.create_("div", self._id + "-wrap", "slider")
        self.slides_navi = Element.create_("div", self._id + "-navi", "prevNext")
        self.slides_navi.element.innerHTML = "\n".join(slides_navi)
        self.slides_wrap.element.innerHTML = "\n".join(cleaned_content)

        console.log("Questing for ", f"#{self.main_div.id}")
        self.main_div.element.innerHTML = "\n".join(slides_headers)
        self.main_div.element.appendChild(self.slides_wrap.element)
        self.main_div.element.appendChild(self.slides_navi.element)
        self.parent.appendChild(self.main_div.element)


console.log("done initializing slides")
