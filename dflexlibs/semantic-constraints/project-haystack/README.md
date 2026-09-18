# Project-Haystack constraints for the DF sequences

Not yet started, and it is still open whether SHACL-style "constraints" are the
right form here at all. The two candidates:

- **Tags directly in the CDL annotation** — a `metadataLanguage="Haystack ..."`
  block on each connector listing the required marker tags, with no separate
  shape library.
- **Xeto specs** — a formal spec per connector. See `../../../../xeto/` and
  `../../../../haystack-defs/`.
