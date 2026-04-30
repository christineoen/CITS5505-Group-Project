# Signup flow — role selection

## Overview

A two-step signup flow where users first choose their role, then complete a profile form tailored to that role.

---

## Step 1 — Role selection

**Heading:** "How can we help?"  
**Subheading:** "Select what brings you here today."

Three selectable cards, stacked vertically. Each card has:
- An icon on the left
- A title and short subtitle in the middle
- A right-arrow chevron on the right

Tapping a card selects it (highlighted state). A "Continue" button below the cards is disabled until a card is selected.

### Cards

| Title | Subtitle | Role value |
|---|---|---|
| I need a babysitter | Find trusted sitters for your family | `parent` |
| I am a babysitter | Create a profile and find families | `sitter` |
| Both | I need childcare and offer it too | `both` |

### Card states
- **Default:** white background, light border
- **Selected:** blue-tinted background, blue border, arrow chevron fills blue
- **Continue button:** disabled/muted until a card is selected, then becomes active

---

## Step 2 — Profile form

A focused form that adapts based on the role selected in step 1.

Includes a back button that returns to step 1.

### Fields

All roles include:
- Name (text)
- Suburb / postcode (text)

Role-specific field:
- `parent` → "Number of children"
- `sitter` → "Years of experience"
- `both` → "Number of children" (parent profile is completed first)

### Headings by role

| Role | Heading | Subheading |
|---|---|---|
| `parent` | Set up your parent profile | Help sitters know a little about your family. |
| `sitter` | Set up your sitter profile | Tell families a bit about yourself. |
| `both` | Let's start with your parent profile | You can set up your sitter profile after. |

---

## Progress indicator

A two-segment progress bar sits below the step label.

- Step 1: first segment filled
- Step 2: both segments filled

---

## Notes for implementation

- The `both` role should complete the parent profile first, then prompt the user to set up their sitter profile after account creation (e.g. a post-signup banner or modal — not a third step in this flow).
- The role value (`parent`, `sitter`, `both`) should be stored and used to determine which profile(s) to scaffold for the new user.
- The back button on step 2 should restore the previously selected card in step 1.
