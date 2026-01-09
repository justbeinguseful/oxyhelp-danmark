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
1. **Hero** - Danish contact point badge, primary CTA "Få dansk tilbud"
2. **Sådan fungerer køb** - 3-step purchase process
3. **Hvorfor Oxyhelp** - Product benefits (EU-made, hard chamber, PVHO, reliability)
4. **Hard vs Soft** - Info box comparing chamber types
5. **For hvilke klinikker** - Target clinic types
6. **Business case** - Investment, financing, break-even info
7. **Hvad vi hjælper med** - Trust blocks (Danish contact, pricing negotiation, financing, showroom)
8. **Showroom** - Copenhagen showroom info
9. **Kontakt** - Simplified form with "Få dansk tilbud" CTA
10. **Thank you page** - `/tak.html` confirmation page

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
- `[2024-12-24]` Major overhaul for Danish lead capture optimization:
  - Updated SEO (title, meta description) for Denmark-focused keywords
  - Changed nav CTA to "Få tilbud (Danmark)"
  - New hero with "Dansk kontaktpunkt" badge and microcopy
  - Added "Sådan fungerer køb" 3-step process section
  - Replaced old process section with "Hvad vi hjælper med" trust blocks
  - Trust card updated: "Vi forhandler en god pris på dine vegne"
  - Simplified contact form (name, email, phone, purpose dropdown)
  - Created thank you page (`tak.html`)
  - Added manufacturer link to footer only
  - Created `/assets/images/` folder for future images
- `[2024-12-12]` Restyled to match Oxyhelp brand (85-90% alignment per designer feedback)
- `[2024-12-12]` Added robots.txt to block search engines during development
- `[2024-12-11]` Initial site creation - complete B2B landing page
