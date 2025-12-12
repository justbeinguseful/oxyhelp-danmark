# CLAUDE.md - Oxyhelp Danmark

## CRITICAL: Read This First

> **BEFORE ANY CHANGES:** Read `../GLOBAL_RULES.md` for cross-site rules!

**Primary Language:** Danish (DA)
**Tone:** Professional B2B, informative, trustworthy

---

## DOMAINS

| Domain | Purpose |
|--------|---------|
| **oxyhelpdanmark.dk** | Primary domain (OxyHelp B2B sales - Denmark) |
| oxyhelpkobenhavn.dk | Geo landing page (Copenhagen-specific) |

**GitHub repo:** `oxyhelp-danmark`
**Netlify site:** `oxyhelp-danmark`

---

## PURPOSE

B2B landing page for Danish clinics interested in purchasing Oxyhelp hyperbaric chambers:
- Help clinic owners understand Oxyhelp products
- Provide business case and financing information
- Generate leads via contact form
- Position as local Danish partner for Oxyhelp

---

## TARGET AUDIENCE

- Clinic owners and decision-makers in Denmark
- Physiotherapy, fertility, sports, wellness, biohacking clinics
- **Private individuals** wanting a chamber for home use
- Looking to add HBOT to their service offering or personal wellness

---

## CONTENT STRUCTURE

### Current Sections
1. **Hero** - Value proposition and CTA
2. **Hvorfor Oxyhelp** - Product benefits (EU-made, hard chamber, PVHO, reliability)
3. **Hard vs Soft** - Info box comparing chamber types
4. **For hvilke klinikker** - Target clinic types
5. **Business case** - Investment, financing, break-even info
6. **Proces** - Step-by-step partnership process
7. **Reference** - Peak Renewal Labs case study
8. **Kontakt** - Netlify-ready contact form

---

## TECHNICAL

- Pure static HTML/CSS (no build step)
- Fira Sans font (matches oxyhelp.com)
- Custom CSS (not Tailwind)
- Netlify Forms with honeypot spam protection
- Mobile responsive

---

## DESIGN

**Style:** Oxyhelp Brand Aligned (85-90%, not clone)

**Colors (from oxyhelp.com):**
- Primary cerulean: #00aeef
- Dark navy: #001d39, #181862
- Light blue backgrounds: #e3f5fe, #c4e2f4

**Elements:**
- Fira Sans font (weights 300-700)
- Pill-shaped buttons (border-radius: 50px)
- Gradient hero with subtle blue radial effects
- Rounded cards (16px border-radius)
- Hover effects with shadows and transforms
- Modern medical-tech aesthetic

**Design Principles (per designer feedback):**
- 85-90% visual alignment with oxyhelp.com, not 100% clone
- Match: font, primary colors, button shapes, section rhythm
- Differentiate: header layout, hero imagery (Nordic context), CTA phrasing (partner-oriented)
- Goal: "Official Nordic partner" not "shadow copy of main site"

---

## CHANGELOG

### December 2024
- `[2024-12-12]` Restyled to match Oxyhelp brand (85-90% alignment per designer feedback)
- `[2024-12-12]` Added robots.txt to block search engines during development
- `[2024-12-11]` Initial site creation - complete B2B landing page
