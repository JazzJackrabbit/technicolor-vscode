<p align="center">
  <img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/banner.png" alt="Technicolor — eight dark themes for Visual Studio Code" width="100%">
</p>

Eight dark themes for Visual Studio Code, drawn from a century of film —
silent-era monochrome, Kodachrome stock, drive-ins, neon signs. Each one
builds on a muted base with one or two strong accents, and styles the full
editor: workbench, syntax, and the integrated terminal.

[Deep](#deep) ·
[Kodachrome](#kodachrome) ·
[Warm](#warm) ·
[Neon](#neon) ·
[Marquee](#marquee) ·
[Drive-In](#drive-in) ·
[Psychedelic](#psychedelic) ·
[Silent Era](#silent-era)

## Themes

### Deep

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-deep.png" alt="Deep — neo-noir, late nights" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-deep.png" alt="Technicolor Deep — Rust" width="100%">

### Kodachrome

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-kodachrome.png" alt="Kodachrome — vintage film stock" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-kodachrome.png" alt="Technicolor Kodachrome — Go" width="100%">

### Warm

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-warm.png" alt="Warm — golden-hour cinematography" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-warm.png" alt="Technicolor Warm — Python" width="100%">

### Neon

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-neon.png" alt="Neon — 80s cyberpunk and synthwave" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-neon.png" alt="Technicolor Neon — TypeScript" width="100%">

### Marquee

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-marquee.png" alt="Marquee — classic Hollywood marquee lights" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-marquee.png" alt="Technicolor Marquee — Svelte" width="100%">

### Drive-In

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-drivein.png" alt="Drive-In — 1950s Americana" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-drivein.png" alt="Technicolor Drive-In — HTML" width="100%">

### Psychedelic

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-psychedelic.png" alt="Psychedelic — 1960s counterculture" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-psychedelic.png" alt="Technicolor Psychedelic — CSS" width="100%">

### Silent Era

<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/card-silentera.png" alt="Silent Era — silver nitrate, title cards" width="100%">
<img src="https://raw.githubusercontent.com/JazzJackrabbit/technicolor-vscode/main/images/screenshot-silentera.png" alt="Technicolor Silent Era — C" width="100%">

## Design

Every variant is built the same way: a tinted near-black base, one or two
strong accents, and a muted supporting palette. All eight themes define the
identical set of 455 workbench color keys, 81 syntax token rules, and 38
semantic token rules — only the colors change — so menus, terminals, charts,
notebooks, and debug icons are themed consistently in every variant. Semantic
highlighting and the full 16-color terminal ANSI palette are covered.

The banner and title cards are generated from the theme files themselves by
[`scripts/build-assets.py`](scripts/build-assets.py), so the artwork always
matches the shipped colors.

## Installation

Install [Technicolor from the Marketplace](https://marketplace.visualstudio.com/items?itemName=oppositefish.technicolor),
or search for "Technicolor" in the Extensions view (`⇧⌘X`). Then open
**Preferences: Color Theme** and pick a variant.

To install from source instead:

```bash
git clone https://github.com/JazzJackrabbit/technicolor-vscode.git
cd technicolor-vscode
npx @vscode/vsce package
code --install-extension technicolor-*.vsix
```

## License

[MIT](LICENSE) © Kirill Ragozin
