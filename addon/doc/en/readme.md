<p align="center">
  <img src="https://www.nvaccess.org/files/nvda/documentation/userGuide/images/nvda.ico" alt="NVDA Logo" width="120">
</p>

# Special Character

<p align="center">Type any special character, anywhere, instantly.</p>

---

<p align="center"><b>author:</b> chai chaimee</p>
<p align="center"><b>url:</b> https://github.com/chaichaimee/SpecialCharacter</p>

---

## Introduction

Special Character is an NVDA add-on that lets you insert symbols and special characters — such as bullets, currency signs, quotation marks, or dashes — with a single keystroke, in almost any application.

Instead of hunting through the Windows Character Map or memorizing obscure Alt-codes, you press a simple Ctrl+number (or Ctrl+- / Ctrl+=) shortcut and the character is typed for you, announced by speech exactly once.

Two independent sets of 12 characters are available, so you can keep two different collections (for example, everyday symbols in one set and less common ones in another) and switch between them instantly. The add-on can also be fully customized through its own panel in NVDA's Settings dialog, and it can be turned on or off on the fly without leaving your current application.

## Hot Keys

> **Ctrl+1** through **Ctrl+9**, **Ctrl+0**, **Ctrl+-**, **Ctrl+=**  
> Single Tap : Insert the character stored in that slot (12 customizable slots) for the currently active set

> **Shift+Windows+|**  
> Single Tap : Insert a vertical bar ( | )

> **Shift+Windows+.**  
> Single Tap : Insert an en dash ( – )

> **Shift+Windows+/**  
> Single Tap : Insert an em dash ( — )

> **Shift+Backspace**  
> Single Tap : Switch between Character Set 1 and Character Set 2  
> Double Tap (within half a second) : Turn the Special Character add-on on or off

## Features

### 1. Twelve-Slot Character Sets (Set 1 and Set 2)

Every character is stored in one of 12 slots, mapped to Ctrl+1, Ctrl+2 … Ctrl+9, Ctrl+0, Ctrl+-, and Ctrl+=. There are two complete sets of these 12 slots, so you can maintain two different symbol collections and flip between them with Shift+Backspace.

Out of the box, some slots already contain ready-to-use characters, for example a bullet (•), a pair of parentheses, the Thai baht sign (฿), and the Euro sign (€) in Set 1, and a single quote, a double quote, and an ellipsis (…) in Set 2. The remaining slots are left for you to fill in with the characters you use most.

### 2. Built-in Settings Panel

The add-on registers its own page directly inside NVDA's Settings dialog (under "Special Character Settings"). From there you can:

* Choose Set 1 or Set 2 from a combo box.
* Type or edit the character assigned to each of the 12 slots in its own text field.
* Switch between sets inside the panel itself; your edits to the set you were viewing are kept automatically when you switch.
* Press OK to save everything to disk in one go.

### 3. Context-Aware Insertion Logic

When you press a shortcut, the add-on looks at the application that currently has focus and chooses the safest way to type the character into it. Step by step, this is what happens:

1. It reads the name of the focused application's module.
2. If the application is Microsoft Word, it first tries to insert the character straight through Word's own object model (Selection.TypeText). This behaves like real typing, never touches the clipboard, and avoids Word's "Paste Options" pop-up. If that call fails, it falls back to copying the character to the clipboard and simulating Ctrl+V.
3. If the application is a web browser (Chrome, Firefox, Brave, Edge, or Safari), characters that are also ordinary keyboard keys — the double quote, forward slash, backslash, period, and vertical bar — are sent directly as a key press. Any other character is copied to the clipboard and pasted after a short 40 millisecond delay, which gives the browser's clipboard reader time to see the updated contents before the paste happens.
4. If a braille display with braille input is connected, the character is sent through the braille input handler instead.
5. If the focused control exposes a direct text-insertion method, the add-on uses that.
6. As a last resort, in any other situation, the character is copied to the clipboard and pasted with a short delay, the same as the browser fallback.

After the character has been inserted, NVDA speaks it exactly once.

### 4. Dual Compatibility With Old and New NVDA Keyboard APIs

On startup, the add-on checks whether the newer `winBindings.user32` keyboard API is available (introduced in 64-bit builds of NVDA 2026.1). If it is, the add-on uses that modern API for any low-level key simulation it needs in Word; otherwise it automatically falls back to the older `winUser` API, so the same shortcuts work correctly on both older and newer, 32-bit and 64-bit, installations of NVDA.

In both cases, the add-on temporarily turns off NVDA's "speak typed characters" option while it inserts a character, then restores your original setting right afterward and speaks the character itself, so you never hear it announced twice.

### 5. Smart Tap Counting on Shift+Backspace

> Pressing Shift+Backspace does not act immediately. Instead, the add-on waits half a second to see whether you press it again:
> 
> * If only one press happens within that half-second window, it switches the active character set (Set 1 ↔ Set 2) and announces which set is now active.
> * If a second press (or more) happens within the same window, it instead toggles the entire add-on on or off, announcing the new state.
> 
> This lets a single, easy-to-remember key combination cover two related actions without needing two separate shortcuts.

### 6. Independent Dash and Bar Shortcuts

Three characters that are commonly needed while writing — the vertical bar, the en dash, and the em dash — have their own dedicated shortcuts (Shift+Windows+|, Shift+Windows+., and Shift+Windows+/) so you don't need to use up a numbered slot for them.

### 7. Persistent, Auto-Migrating Configuration

Your character sets are saved as a JSON file named `specialCharacters.json` inside a `ChaiChaimee` subfolder of your NVDA user configuration folder, so your custom characters are kept between NVDA sessions and updates.

If the add-on detects a configuration file left over from an older version directly in the main NVDA configuration folder, it automatically copies its contents into the new subfolder location and only removes the old file once the copy has been verified, so your existing customizations are never lost during an upgrade.

### 8. Enable / Disable Without Losing Settings

Turning the add-on off (via a double tap of Shift+Backspace) simply stops it from responding to the character shortcuts; your configured sets remain saved and are used again as soon as you turn the add-on back on.

> **Note:** The character-insertion shortcuts (Ctrl+1–0, Ctrl+-, Ctrl+=) are only available while the add-on is enabled. If nothing happens when you press one, check whether the add-on has been turned off with a double tap of Shift+Backspace.

## Support Me

If this tool has made your life easier, consider fueling the next update with a small donation.

<p align="center">
  <a href="https://buy.stripe.com/dRm9AU1xQ3Ds22N6VK1VK01">
    <img src="https://img.shields.io/badge/Donate-Support%20Me-blue?style=for-the-badge&logo=stripe" alt="Support me">
  </a>
</p>

Your support means the world. Let's build something great together

---

© 2026 Chai Chaimee NVDA Add-on Released under GNU GPL