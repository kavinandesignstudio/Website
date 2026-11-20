"""
Hand-drawn line illustrations for the Kavinan Design Studio website.

Every sketch is an inline SVG drawn with strokes only, so it:
  • takes the page's text colour (works in light and dark mode),
  • "draws itself" when scrolled into view (site.js animates each stroke),
  • stays tiny (no image files).
Strokes with class="ac" are drawn in the brand orange.
"""

SKETCHES = {
    # Stacked hill house with stilts, jaali and sloping canopy (Strata-like)
    "architecture": """
<path d="M8 146H232"/>
<path d="M44 146V120M78 146V120M112 146V120"/>
<path d="M34 120H134V86H34Z"/>
<path d="M44 96H66V112H44ZM82 96H118V112H82Z"/>
<path d="M78 86H178V54H78Z"/>
<path d="M88 62H112V78H88ZM120 62H136V78H120Z"/>
<path d="M146 60H170V82H146ZM152 60V82M158 60V82M164 60V82M146 66H170M146 72H170M146 78H170"/>
<path d="M70 48L188 36M74 54L70 48M182 54L188 36"/>
<path d="M134 120L168 86M140 120V114H146V108H152V102H158V96H164V90"/>
<path d="M210 146V110M198 116C190 104 200 90 210 96C216 86 232 92 228 104C236 112 226 124 214 120C206 128 194 124 198 116Z"/>
<circle class="ac" cx="38" cy="34" r="10"/>
<path class="ac" d="M20 146C40 140 60 152 80 146"/>""",

    # One-point perspective living room with sofa, pendant, plant
    "interior": """
<path d="M72 34H168V104H72Z"/>
<path d="M72 34L20 8M168 34L220 8M72 104L20 152M168 104L220 152"/>
<path d="M98 46H142V80H98ZM120 46V80M98 63H142"/>
<path d="M84 120H156V106H84ZM80 104V124M160 104V124M84 106V98H156V106"/>
<path d="M120 0V22"/>
<path class="ac" d="M110 22H130L126 30H114Z"/>
<path class="ac" d="M104 38L112 32M136 38L128 32" />
<path d="M186 132H200L198 148H188Z"/>
<path d="M193 132C186 120 180 116 176 106M193 132C194 118 200 110 206 104M193 132C198 124 208 122 214 116"/>
<ellipse cx="120" cy="138" rx="46" ry="8"/>
<path d="M36 64V112M36 64H52V112"/>""",

    # Terrain, tree, winding path, pond, sun
    "landscape": """
<path d="M4 120C40 104 70 112 100 102C134 90 170 100 236 84"/>
<path d="M4 134C46 120 82 128 120 118C156 108 196 116 236 104"/>
<path d="M4 148C52 138 92 144 140 134C180 126 210 132 236 124"/>
<path d="M60 150C80 136 96 130 120 128C150 126 160 116 176 100"/>
<path d="M64 150C86 140 102 136 124 134C152 132 166 122 182 104"/>
<path d="M150 98V62M150 72L138 60M150 80L164 66"/>
<path d="M126 58C118 40 136 26 150 32C160 18 186 26 182 44C194 54 182 72 166 66C156 78 132 74 126 58Z"/>
<path d="M40 104V84M30 88C26 78 34 70 40 74C46 66 58 72 54 82C60 90 50 96 42 92C36 98 28 94 30 88Z"/>
<ellipse cx="200" cy="130" rx="26" ry="7"/>
<path d="M190 130H210"/>
<circle class="ac" cx="204" cy="30" r="12"/>
<path class="ac" d="M204 8V2M226 30H232M188 14L184 10M220 14L224 10"/>""",

    # Programme (Gantt) + clipboard checklist
    "project-management": """
<path d="M20 20V140H170"/>
<path d="M20 44H34M20 68H34M20 92H34M20 116H34" />
<path d="M36 36H82V50H36Z"/>
<path d="M70 60H120V74H70Z"/>
<path class="ac" d="M104 84H150V98H104Z"/>
<path d="M138 108H166V122H138Z"/>
<path d="M82 43L94 43L94 67M120 67L130 67L130 91M150 91L156 91L156 115" stroke-dasharray="3 4"/>
<path d="M182 30H232V146H182Z"/>
<path d="M196 24H218V36H196Z"/>
<path d="M192 56L198 62L208 50M214 56H226M192 82L198 88L208 76M214 82H226M192 108H208M214 108H226M192 130H208M214 130H226"/>
<path class="ac" d="M192 104L200 112M200 104L192 112"/>""",

    # Tower crane, house going up, handover key
    "design-build": """
<path d="M6 148H234"/>
<path d="M40 148V22M52 148V22M40 22H52M40 40L52 52M52 40L40 64M40 76L52 88M52 76L40 100M40 112L52 124M52 112L40 136"/>
<path d="M20 22H190M40 10L46 22M46 10L52 22M46 10H52"/>
<path d="M46 10L120 22M46 10L28 22"/>
<path d="M150 22V54"/>
<path class="ac" d="M140 54H160V66H140Z"/>
<path d="M96 148V104L136 76L176 104V148Z"/>
<path d="M126 148V122H146V148M104 112H118V124H104Z"/>
<circle class="ac" cx="206" cy="112" r="11"/>
<path class="ac" d="M206 123V148M206 132H214M206 140H212"/>""",

    # Open-to-sky courtyard (mutram) with timber pillars and sunken court
    "courtyard": """
<path d="M20 30H220M20 30L50 52H190L220 30"/>
<path d="M50 52V60H190V52"/>
<path d="M58 60V128M182 60V128M86 64V116M154 64V116"/>
<path d="M54 128H62M178 128H186M83 116H89M151 116H157"/>
<path d="M54 64H62M178 64H186"/>
<path d="M20 30V150M220 30V150"/>
<path d="M20 150H220"/>
<path d="M62 128H178L162 116H78Z"/>
<path d="M78 116L86 110H154L162 116"/>
<path d="M112 108H128V96H112Z"/>
<path d="M120 96C114 90 112 82 120 76C128 82 126 90 120 96Z"/>
<path class="ac" d="M80 6L98 30M120 2V30M160 6L142 30"/>
<path class="ac" d="M204 120C196 120 196 100 204 96C212 100 212 120 204 120Z"/>""",

    # Small process sketches
    "p-site": """
<path d="M6 104C40 90 70 98 100 86C130 74 170 82 234 66"/>
<path d="M6 122C44 108 80 116 118 104C150 94 190 100 234 88"/>
<path d="M6 140C50 128 92 134 136 124C174 116 206 120 234 110"/>
<circle cx="170" cy="40" r="26"/>
<path class="ac" d="M170 20L176 40L170 60L164 40Z"/>
<path d="M170 10V16M170 64V70M140 40H146M194 40H200"/>""",
    "p-concept": """
<path d="M30 120C50 70 80 60 100 90C120 120 150 60 180 50"/>
<path d="M40 136C80 126 120 132 170 122"/>
<path class="ac" d="M150 20L210 80L200 90L140 30Z"/>
<path d="M140 30L134 18L150 20"/>
<circle cx="70" cy="40" r="14"/>""",
    "p-3d": """
<path d="M120 20L196 60V128L120 150L44 128V60Z"/>
<path d="M44 60L120 98L196 60M120 98V150"/>
<path class="ac" d="M120 20L120 98"/>
<path d="M82 79V139M158 79V139" stroke-dasharray="3 5"/>""",
    "p-drawings": """
<path d="M40 40H200V130H40Z"/>
<path d="M40 86H120V130M120 40V70H200M150 70V130"/>
<path d="M40 24H200M40 18V30M200 18V30M120 18V30"/>
<path d="M216 40V130M210 40H222M210 130H222"/>
<path class="ac" d="M70 112A16 16 0 0 1 86 96"/>""",
    "p-handover": """
<circle class="ac" cx="70" cy="80" r="26"/>
<circle cx="70" cy="80" r="9"/>
<path d="M96 80H210M190 80V100M172 80V96M210 80V92"/>
<path d="M40 140H200" stroke-dasharray="4 6"/>""",
}

SERVICE_SKETCH = {
    "architecture": "architecture",
    "interior-design": "interior",
    "landscape": "landscape",
    "project-management": "project-management",
    "design-build": "design-build",
}

PROCESS_SKETCH = ["p-site", "p-concept", "p-3d", "p-drawings", "p-handover"]


def sketch(name, cls="", label=""):
    """Inline SVG for a named sketch. Decorative unless a label is given."""
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return (f'<svg class="sketch {cls}" viewBox="0 0 240 160" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" {aria}>{SKETCHES[name]}</svg>')
