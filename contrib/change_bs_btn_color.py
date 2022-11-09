#!/usr/bin/env python3

button = 'primary'
color = '#6f42c1'


def hex_to_rgb(h):
  return tuple(str(int(h[i:i + 2], 16)) for i in (1, 3, 5));


print(f''':root {{
  --bs-{button}: {color};
  --bs-{button}-rgb: {', '.join(hex_to_rgb(color))};
}}

.btn-{button} {{
  --bs-btn-color: #fff;
  --bs-btn-disabled-color: #fff;
  --bs-btn-hover-color: #fff;
  --bs-btn-active-color: #fff;

  --bs-btn-bg: {color};
  --bs-btn-disabled-bg: {color};
  --bs-btn-hover-bg: shade-color(var(--bs-primary), 15%)
  --bs-btn-active-bg: shade-color(var(--bs-primary), 20%)

  --bs-btn-border-color: {color};
  --bs-btn-disabled-border-color: {color};
  --bs-btn-hover-border-color: shade-color(var(--bs-primary), 20%)
  --bs-btn-active-border-color: shade-color(var(--bs-primary), 25%)

  --bs-btn-focus-shadow-rgb: to-rgb(tint-color(var(--bs-primary), 15%));
}}''')
