# Photo Tools GUI

A **CustomTkinter-based desktop photo management app** with a 3-panel layout (folder tree | thumbnail grid | preview pane).

## Architecture (MVC-like)

| Layer | Location | Purpose |
|---|---|---|
| **Model** | `core/` | Business logic: EXIF read/write (`exif_handler.py`), photo indexing (`photo_manager.py`), date/metadata sorting (`sorter.py`), file move/copy (`organizer.py`), hash-based dedup (`deduplication.py`), settings persistence (`settings.py`) |
| **View** | `gui/panels/` | Three resizable panels: `FolderTreePanel`, `ThumbnailGridPanel`, `PreviewPanePanel` |
| **Controller** | `gui/app.py` + `gui/dialogs/` | `PhotoToolsApp` orchestrates panels; dialogs for sort, dedup, EXIF edit, move/copy, metadata filter |
| **Utilities** | `utils/` | Thumbnail generation/caching (`thumbnail_generator.py`), file helpers (`file_utils.py`) |

## Key Features

- Browse folders, view photo thumbnails (batch-loaded 30 at a time), multi-select
- Full EXIF metadata display and star-rating editing (supports HEIC via `pillow-heif`, falls back to `exiftool`)
- Sort photos into `YYYY/MM/DD` folder structures by EXIF date
- SHA-256 duplicate detection with threaded scanning + progress
- Filter thumbnails by camera make/model/min rating
- Draggable panel dividers, dark/light mode, toast notifications

## Dependencies

`customtkinter`, `Pillow`, `pillow-heif`, `pyexiv2` (optional: `exiftool` for HEIC EXIF writing)

## Quick Start

```bash
make run
```

Or manually:

```bash
make venv
make deps
python main.py
```

## Project Structure

```
ui-poc-1/
├── main.py                  # Entry point
├── Makefile                 # Build/run automation
├── requirements.txt         # Python dependencies
├── core/                    # Backend business logic
│   ├── settings.py          # Settings persistence (JSON)
│   ├── exif_handler.py      # EXIF read/write
│   ├── photo_manager.py     # Photo indexing
│   ├── sorter.py            # Date/metadata sorting
│   ├── organizer.py         # Move/copy operations
│   └── deduplication.py     # Hash-based dedup
├── gui/                     # UI layer
│   ├── app.py               # Main application window
│   ├── panels/
│   │   ├── folder_tree.py   # Left panel: folder navigation
│   │   ├── thumbnail_grid.py # Center panel: thumbnail grid
│   │   └── preview_pane.py  # Right panel: image preview
│   ├── dialogs/
│   │   ├── exif_editor.py           # EXIF rating editor
│   │   ├── sort_dialog.py           # Sort by date dialog
│   │   ├── move_dialog.py           # Move/copy dialog
│   │   ├── deduplication_dialog.py  # Duplicate finder/remover
│   │   └── metadata_filter_dialog.py # Filter by metadata
│   └── widgets/
│       ├── status_bar.py      # Status bar + toast notifications
│       └── panel_divider.py   # Draggable panel divider
└── utils/
    ├── file_utils.py           # File utility functions
    └── thumbnail_generator.py  # Thumbnail generation/caching
```

## Notes

- **Threading**: Deduplication scanning runs in a background daemon thread with progress callbacks marshalled to the UI thread via `after(0, ...)`.
- **Batch loading**: Thumbnails are loaded 30 at a time using `after()` scheduling to keep the UI responsive.
- **Graceful degradation**: EXIF handling degrades gracefully if `pyexiv2`/`exiftool` are unavailable.
- **Thumbnail caching**: Thumbnails are cached as PNGs under `~/.cache/photo-tools/thumbnails/`.

## Known Issues

- The `SUPPORTED_EXTENSIONS` set is duplicated across multiple files (`core/photo_manager.py`, `gui/panels/thumbnail_grid.py`, `core/deduplication.py`, `gui/dialogs/sort_dialog.py`, `utils/file_utils.py`).
