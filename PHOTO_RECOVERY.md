# Missing photograph recovery — Ionian Sanctuary v1.3.2

The four JPEGs are **genuine, publicly licensed historical-site and artefact photographs**. The evaluation will not create an offline ZIP until they are physically saved under `photos/` with the exact names below.

## Recommended recovery: manually download and import

From the extracted `IONIAN_ARCH_EVAL_v1_3_1` folder, double-click `GET_PHOTOS_WINDOWS.cmd`, or run in PowerShell:

```powershell
.\IMPORT_PHOTOS_WINDOWS.cmd
```

The importer makes **no network requests**. It validates the selected files as JPEGs, copies them to `photos/` under the exact required names, and records hashes. It does not verify the photographic subject; confirm each saved JPEG matches its credited Commons page.

## If automatic retrieval fails

Open these verified Wikimedia Commons file pages in Chrome or Edge. Click the **960-pixel preview** or an available **960px** resolution in the image description (avoid saving the HTML web page). Right-click the **actual image** and choose **Save image as...**. Save the original JPEG anywhere (for example Downloads). Then double-click `IMPORT_PHOTOS_WINDOWS.cmd` and select the JPEG in the file chooser. The importer saves it inside `photos/` with the exact required name.

| Save as | Wikimedia Commons source | Credit / license |
| --- | --- | --- |
| `claros_temple.jpg` | [Claros, Doric Temple of Apollo, southeast view](https://commons.wikimedia.org/wiki/File:View_of_the_ruins_of_the_Doric_Temple_of_Apollo_from_the_southeast,_Claros,_Ionia,_Turkey.jpg) | Carole Raddato, CC BY-SA 2.0 |
| `notion_athena.jpg` | [Temple of Athena at Notion 4](https://commons.wikimedia.org/wiki/File:The_Temple_of_Athena_at_Notion_4.jpg) | Isabeau, CC BY-SA 4.0 |
| `notion_theatre.jpg` | [Notion theatre 6](https://commons.wikimedia.org/wiki/File:Notion_theatre_6.jpg) | Isabeau, CC BY-SA 4.0 |
| `apollo_comparative.jpg` | [Roman radiate of Aurelian, FindID 516806](https://commons.wikimedia.org/wiki/File:Roman_Coin,_Radiate_of_Aurelian_(FindID_516806).jpg) | Portable Antiquities Scheme / Trustees of the British Museum, CC BY-SA 4.0 |

**Note:** The Aurelian coin is a comparative object **from Britain**, not a Claros excavation find or RPC type cited in the tasks. See `PHOTOGRAPH_CREDITS.md` for complete credits.

Expected structure:

```text
IONIAN_ARCH_EVAL_v1_3_1/
  photos/
    manifest.json
    claros_temple.jpg
    notion_athena.jpg
    notion_theatre.jpg
    apollo_comparative.jpg
```

Check the saved files:

```powershell
Get-ChildItem .\photos\*.jpg | Select-Object Name,Length
.\IMPORT_PHOTOS_WINDOWS.cmd
.\BUILD_OFFLINE_WINDOWS.cmd
```

All four images must be actual JPEG binaries, not browser HTML pages renamed `.jpg`. The builder checks the JPEG signatures. The `photos/download_integrity.json` file records cryptographic checksums for reproducibility.

## Conditions and caveats

Use original or Wikimedia-hosted resized JPEGs, maintaining source credit and the Creative Commons license links. The supplied images illustrate context; they do not establish excavation provenience of a catalogue specimen. The package is not fully offline until all four photographs are present.
