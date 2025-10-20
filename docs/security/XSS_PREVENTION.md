# XSS Prevention Guidelines for OBCMS

This document provides comprehensive guidelines for preventing Cross-Site Scripting (XSS) vulnerabilities in the OBCMS system.

## Overview

Cross-Site Scripting (XSS) is a critical web security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. This can lead to:

- Session hijacking (cookie theft)
- Keylogging and form hijacking
- Website defacement
- Credential theft
- Malware distribution

## Key Principles

### 1. Never Trust User Input

**Rule:** Always assume user input is malicious unless explicitly validated and sanitized.

All data from:
- URL parameters
- Form submissions
- Database records (user-submitted content)
- API responses from external sources
- Request headers

Must be treated as potentially dangerous.

### 2. Context-Specific Encoding

Different contexts require different encoding strategies:

**HTML Context:** HTML entity encoding
**JavaScript Context:** JavaScript escaping
**URL Context:** URL encoding
**CSS Context:** CSS escaping

## Patterns and Solutions

### Pattern 1: Safe Text Content (Most Common)

**When to use:** Displaying plain text that doesn't need HTML formatting

**WRONG (Vulnerable):**
```javascript
element.innerHTML = userInput;  // Dangerous!
```

**RIGHT (Secure):**
```javascript
element.textContent = userInput;  // Auto-escapes HTML
```

**Why:** `textContent` treats all content as plain text and automatically escapes HTML metacharacters.

### Pattern 2: Building HTML Structure Securely

**When to use:** When you need to create HTML structure with user-provided data

**WRONG (Vulnerable):**
```javascript
container.innerHTML = `
    <div class="card">
        <h3>${title}</h3>
        <p>${description}</p>
    </div>
`;
```

**RIGHT (Secure):**
```javascript
const card = document.createElement('div');
card.className = 'card';

const heading = document.createElement('h3');
heading.textContent = title;  // Safe
card.appendChild(heading);

const paragraph = document.createElement('p');
paragraph.textContent = description;  // Safe
card.appendChild(paragraph);

container.appendChild(card);
```

**Why:** Using `createElement()` and `textContent` ensures user data is never parsed as HTML.

### Pattern 3: Django Template Context

**When to use:** In Django templates where server-side rendering happens

**WRONG (Vulnerable):**
```django
{# Auto-disable template escaping - DANGEROUS #}
{{ user_data|safe }}
```

**RIGHT (Secure):**
```django
{# Use automatic escaping (default) #}
{{ user_data }}  {# Automatically escaped #}

{# Or explicitly escape for clarity #}
{{ user_data|escape }}
```

**Why:** Django's automatic escaping (enabled by default) converts HTML special characters to entities.

### Pattern 4: Safe HTML Structure (When Needed)

**When to use:** When user data MUST support limited HTML formatting

**WRONG (Vulnerable):**
```python
from django.utils.html import mark_safe

# DO NOT DO THIS - content from user!
safe_html = mark_safe(f"<b>{user_input}</b>")
```

**RIGHT (Secure):**
```python
from django.utils.html import format_html, escape

# Escape user data FIRST, then mark structure safe
safe_html = format_html(
    "<b>{}</b>",
    escape(user_input)  # Escape user content
)
```

**Why:** `format_html()` automatically escapes all arguments, preventing XSS.

### Pattern 5: Using SafeDOM Utilities (Global)

**When to use:** Complex dynamic content generation

**Implementation:**
```javascript
// Available globally in OBCMS
window.SafeDOM.setText(element, userText);
window.SafeDOM.createElement('div', 'my-class', userText);
window.SafeDOM.escape(userInput);
```

## Django-Specific Guidelines

### Template Escaping

Django templates automatically escape output by default:

```django
{# These are ALL safe - HTML is automatically escaped #}
{{ user.name }}
{{ post.title }}
{{ comment.content }}
```

### Disabling Escaping (Rarely Needed)

Only disable escaping when you KNOW the content is safe:

```django
{# For content you control (not user input) #}
{% autoescape off %}
    {{ safe_html_from_database }}
{% endautoescape %}
```

### Safe String Types

```python
from django.utils.safestring import mark_safe
from django.utils.html import format_html

# Good: format_html escapes all arguments
safe = format_html("<b>{}</b>", user_name)

# Acceptable: mark_safe() for developer-controlled HTML
safe = mark_safe("<b>This is our content</b>")

# BAD: Don't do this
safe = mark_safe(f"<b>{user_input}</b>")  # XSS!
```

## JavaScript Security

### innerHTML vs. textContent

**innerHTML:** Can execute scripts if content contains `<script>` tags
**textContent:** Always treats content as plain text

```javascript
// WRONG
element.innerHTML = userInput;

// RIGHT
element.textContent = userInput;
```

### Event Listeners (Safe)

Attach listeners programmatically instead of via `onclick` attributes:

```javascript
// WRONG
element.innerHTML = `<button onclick="deleteItem()">Delete</button>`;

// RIGHT
const button = document.createElement('button');
button.textContent = 'Delete';
button.addEventListener('click', deleteItem);
element.appendChild(button);
```

### Template Literals (Be Careful)

Template literals don't automatically escape:

```javascript
// WRONG
const html = `<div>${userInput}</div>`;
container.innerHTML = html;  // XSS if userInput has HTML

// RIGHT
const div = document.createElement('div');
div.textContent = userInput;
container.appendChild(div);
```

## Common XSS Payloads (For Testing)

Use these to test your security measures:

```html
<!-- Script injection -->
<script>alert('XSS')</script>

<!-- Event handler injection -->
<img src=x onerror=alert('XSS')>

<!-- SVG injection -->
<svg><script>alert('XSS')</script></svg>

<!-- Data attribute -->
<a href="javascript:alert('XSS')">Click</a>

<!-- Form action -->
<form action="javascript:alert('XSS')"><input type="submit"></form>

<!-- Style injection -->
<style>body{background:url('javascript:alert(\"XSS\")')}</style>
```

**Note:** If any of these payloads execute when user data is displayed, you have an XSS vulnerability.

## Content Security Policy (CSP)

OBCMS implements CSP in production to provide defense-in-depth:

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' https://trusted-cdn.com;
    img-src 'self' data: https:;
    ...
">
```

CSP prevents inline scripts from executing, even if an XSS payload slips through.

## Input Validation

While encoding is the primary defense, validation provides additional protection:

**Good validation:**
```python
# Only allow expected formats
if not re.match(r'^\d{4}-\d{2}-\d{2}$', user_date):
    raise ValidationError("Invalid date format")

# Whitelist characters
if not all(c.isalnum() or c in '-_ ' for c in username):
    raise ValidationError("Invalid characters")
```

**Insufficient validation:**
```python
# This is NOT sufficient - user can still bypass with encoding
if '<script>' not in user_input:
    safe = user_input  # Still vulnerable!
```

## File Upload Security

User-uploaded files can contain XSS:

```python
# WRONG - Don't trust file extensions
if filename.endswith('.jpg'):
    save_file(file_content)  # Could be SVG with script!

# RIGHT - Validate MIME type and content
import magic
mime_type = magic.from_buffer(file_content, mime=True)
if mime_type not in ALLOWED_TYPES:
    reject_file()
```

## Testing for XSS

### Manual Testing

1. Identify all user input fields
2. Test with XSS payloads (see Common Payloads section)
3. Check browser developer console for errors
4. Verify no JavaScript executes

### Automated Testing

```python
# Run security tests
python manage.py test common.tests.test_xss_security -v 2
```

### Browser Testing

1. Open DevTools
2. Try XSS payloads in form fields
3. Check Network tab for suspicious requests
4. Monitor Console for errors

## Code Review Checklist

When reviewing code for XSS vulnerabilities:

- [ ] All user input displayed uses `textContent` or template escaping
- [ ] `innerHTML` only used with developer-controlled content
- [ ] No `mark_safe()` without explicit `escape()` of user data
- [ ] No template variables with `|safe` unless necessary
- [ ] Event listeners attached programmatically, not via HTML attributes
- [ ] Form validation exists (though not as primary defense)
- [ ] CSP headers configured correctly
- [ ] File uploads validated for type and content
- [ ] URL parameters escaped in all contexts

## Common Mistakes to Avoid

### Mistake 1: Escaping Too Late

```python
# WRONG - HTML already contains script by the time we escape
user_input = "<script>alert('XSS')</script>"
html = f"<div>{user_input}</div>"
escaped = escape(html)  # Too late!
```

### Mistake 2: Trusting Frontend Validation

```javascript
// WRONG - User can disable JavaScript or modify requests
if (userInput.match(/^[a-zA-Z]+$/)) {
    sendToServer(userInput);  // Attacker can still send script
}
```

Always validate on the server.

### Mistake 3: Double Encoding

```python
# WRONG - Creates invalid display
escaped_once = escape(user_input)
escaped_twice = escape(escaped_once)  # Now displays &amp;lt;
```

### Mistake 4: Selective Escaping

```python
# WRONG - Attacker can use characters you didn't escape
if '<' not in user_input:
    safe = user_input  # But onclick= still works!
```

Escape ALL HTML special characters.

### Mistake 5: Context Confusion

```python
# WRONG - HTML escape insufficient for JavaScript context
from django.utils.html import escape
user_input = "'; alert('XSS'); //"
javascript = f"var name = '{escape(user_input)}';"  # Still vulnerable!
```

Use context-specific encoding.

## Resources

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/#cross-site-scripting-xss-protection)
- [MDN XSS Article](https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting_XSS)
- [CWE-79: XSS](https://cwe.mitre.org/data/definitions/79.html)

## Incident Response

If an XSS vulnerability is discovered:

1. **Immediate:** Take affected page offline if possible
2. **Assessment:** Determine scope - what data could be compromised?
3. **Notification:** Alert users if personal data may be affected
4. **Fix:** Apply the appropriate secure pattern from this guide
5. **Testing:** Verify fix with security tests
6. **Monitoring:** Watch for exploitation attempts in logs

## Questions?

If you're unsure whether code is vulnerable:

1. Check this guide first
2. Ask in code review
3. Run security tests
4. Contact the security team

Remember: **When in doubt, escape it out!**
