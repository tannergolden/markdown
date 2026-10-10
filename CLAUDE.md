# Markdown Kit: notes for Claude

Standing rules from the owner, for every session that works on this repository.

## Collections are drawn by one hand

Every collection the kit draws, the medieval one and every one after it, must read as the work of one artist:
twelve different worlds drawn by the same hand.

- Before starting or changing a collection, read
  [ADR-0007](docs/adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md) and
  [Drawing a Collection](docs/technical/Collections.md).
- Define a new collection's hand in `src/domain/collections/hand.py` before its first design: its inks, ground
  bands, flame, moon, skin, glint and month's mark.
- Every design subclasses `CollectionSet` and passes `check`; the tests hold every design to its hand.
- Review every design at 1x beside the other eleven, by day and by night, wide and on a phone.
  - Fix the weakest first.
  - Keep passing until no design stands apart from its year.
- The bar, in the owner's words: "make sure they are absolutely badass and anyone viewing it would be AMAZED!"

## Working here

- The kit is standard-library Python. Run Python with the GitHub tokens unset:
  `env -u GH_TOKEN -u GITHUB_TOKEN -u MARKDOWN_TOKEN ...`.
- `make lint` and `make test` must pass before a push, and `make themes` redraws `docs/themes` after a theme
  changes.
- Commits follow [CONTRIBUTING](.github/CONTRIBUTING.md): Conventional Commits with an emoji, signed off.
