# Codebase Extractor

A simple Python tool to extract and combine code from an entire codebase into a single text file for simplifying workflows when using LLM's. If i get feedback that this is useful, I'll add more features and probably make a free mac app out of it.

## Features

- 📂 **Complete Directory Traversal** - Scans your entire codebase (all directories and subdirectories)
- 🚫 **Customizable Exclusions** - Skip specific file types or directories
- 🌳 **Directory Tree Visualization** - See your project structure at a glance
- 📝 **Accurate Token Counting** - OpenAI-compatible token counting with tiktoken
- 🖥️ **Console Feedback** - Visual progress indicators during processing
- ⚙️ **Flexible Configuration** - Command-line arguments for easy customization
- 🛡️ **Safe Extraction** - Prevents recursively indexing previous extraction files
- 📎 **Selective Inclusion** - Include only specified files/folders while maintaining full structure
- 🔄 **Cross-platform** - Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.6 or higher

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/codebase_extractor.git
cd codebase_extractor
```

### Recommended Optional Dependencies

For the best experience, install these optional dependencies:

```bash
# For progress bars
pip install tqdm

# For accurate OpenAI-compatible token counting
pip install tiktoken
```

## Usage

### Basic Usage

```bash
python codebase_extractor.py
```

This will extract all files from the current directory (excluding default binary files and system directories) and save them to `codebase_extract.txt`.

### Custom Usage

```bash
python codebase_extractor.py --root /path/to/your/project --output project_extract.txt --exclude "*.log" --exclude "temp/" --force
```

### Selective Content Inclusion

To include only specific files and folders in the content (while still mapping the entire directory structure):

```bash
# Include specific files and an entire folder (with all its subfolders)
python codebase_extractor.py --include "README.md src/main.py src/core/"

# OR comma-separated list
python codebase_extractor.py --include "README.md,src/main.py,src/core/"
```

When you specify a folder path (with or without a trailing slash), the script will include all files in that folder and all its subfolders.

### Accurate Token Counting

For accurate token counting compatible with OpenAI models:

```bash
# First, install tiktoken
pip install tiktoken

# Then specify which model's tokenizer to use
python codebase_extractor.py --model "gpt-4"
```

Available models include `gpt-4`, `gpt-3.5-turbo`, `text-embedding-ada-002`, and others supported by tiktoken.

### Command-line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--root` | `-r` | Root directory to start extraction (default: current directory) |
| `--output` | `-o` | Output file name (default: codebase_extract.txt) |
| `--exclude` | `-e` | Exclude patterns (can be used multiple times) |
| `--include` | `-i` | Only include content for specific files/folders (space or comma separated) |
| `--model` | `-m` | Model to use for token counting (default: gpt-4) |
| `--no-defaults` | | Don't use default exclusions |
| `--no-progress` | | Don't show progress bar |
| `--force` | `-f` | Force overwrite if output file exists (skips confirmation prompt) |

## Exclude Patterns

You can exclude files and directories using patterns:

- `*.ext` - Exclude all files with the extension `.ext`
- `dir_name/` - Exclude directory named `dir_name`
- `filename` - Exclude files named `filename`

Multiple exclusion patterns can be specified by using the `--exclude` option multiple times:

```bash
python codebase_extractor.py --exclude "*.log" --exclude "temp/" --exclude "node_modules/"
```

The script comes with sensible default exclusions for common binary files (images, executables, etc.) and system directories (`.git`, `node_modules`, etc.). You can disable these defaults with the `--no-defaults` flag.

## Include Patterns

You can specify which content to include in several ways:

- Individual files:
  - `filename.ext` - Just the filename (will match in any directory)
  - `dir/filename.ext` - Relative path from the root directory
  - `*.py` - Wildcard pattern to include all Python files
  - `models/*.py` - Wildcard pattern to include Python files in a specific directory

- Entire directories:
  - `src/core/` - Include all files in the core directory and its subdirectories
  - `src/core` - Same as above (trailing slash is optional for directories)

Include patterns can be specified as space-separated or comma-separated lists:

```bash
# Space-separated (enclose in quotes)
python codebase_extractor.py --include "README.md src/index.ts src/core/ src/tools/base-tool.ts"

# Comma-separated
python codebase_extractor.py --include "README.md,src/index.ts,src/core/,src/tools/base-tool.ts"
```

## Token Counting with tiktoken

The script uses OpenAI's `tiktoken` library for accurate token counting when available:

- Counts tokens exactly as they would be counted by OpenAI's API
- Supports different models (gpt-4, gpt-3.5-turbo, etc.)
- Falls back to whitespace-based counting if tiktoken is not installed

This helps you accurately predict costs when using the extracted file with OpenAI's models.

```bash
# Count tokens for GPT-4
python codebase_extractor.py --model "gpt-4"

# Count tokens for GPT-3.5 Turbo
python codebase_extractor.py --model "gpt-3.5-turbo"
```

## Example Use Case

Imagine you're working on a feature in the `src/core/` module and want to consult an LLM. You can create an extract with:

```bash
python codebase_extractor.py --include "README.md,src/index.ts,src/core/,src/tools/base-tool.ts" --model "gpt-4"
```

This will:
1. Map your entire project structure (for context)
2. Include content from:
   - README.md
   - src/index.ts
   - ALL files in src/core/ and ALL its subdirectories
   - src/tools/base-tool.ts
3. Count tokens accurately for GPT-4, so you know exactly how much it will cost

Perfect for focused AI assistance with optimal token usage!

## Smart Prevention of Self-Indexing

The tool automatically prevents indexing its own output files:

- Automatically excludes the output file from the indexing process
- Detects previous extraction files with the same name
- Prompts for confirmation before overwriting (unless `--force` is used)

This prevents recursive indexing problems and improves overall reliability.

## Example Output

The generated file will have this structure:

```
Total Tokens: 12345 (counted with tiktoken using gpt-4 model)

Note: Only selected files are included with content. Inclusion patterns: README.md, src/index.ts, src/core/, src/tools/base-tool.ts

Directory Structure:

├── README.md
├── package.json
├── src
│   ├── index.ts
│   ├── core
│   │   ├── config.ts
│   │   ├── models
│   │   │   └── user.ts
│   │   └── services
│   │       └── auth.ts
│   └── tools
│       ├── base-tool.ts
│       └── specific-tool.ts
└── tests
    └── core
        └── user.test.ts

Files With Content Included:

- README.md
- src/index.ts
- src/core/config.ts
- src/core/models/user.ts
- src/core/services/auth.ts
- src/tools/base-tool.ts

================================================================================
README.md
================================================================================
# Project Title

This is a sample project...
```

## Default Exclusions

By default, the tool excludes common binary files and system directories:

- Binary files: `.pyc`, `.exe`, `.dll`, `.jpg`, `.png`, etc.
- System directories: `.git`, `.svn`, `__pycache__`, `node_modules`, etc.

The complete list of default exclusions includes:

```python
DEFAULT_EXCLUSIONS = [
    '*.pyc', '*.pyo', '*.so', '*.o', '*.a', '*.dll', '*.lib', '*.dylib',
    '*.exe', '*.bin', '*.pkl', '*.dat', '*.db', '*.sqlite', '*.sqlite3',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.svg', '*.ico',
    '*.mp3', '*.mp4', '*.wav', '*.flac', '*.ogg', '*.avi', '*.mov',
    '*.zip', '*.tar', '*.gz', '*.bz2', '*.xz', '*.rar', '*.7z',
    '*.pdf', '*.doc', '*.docx', '*.ppt', '*.pptx', '*.xls', '*.xlsx', '.env',
    '.git/', '.svn/', '.hg/', '.idea/', '.vscode/', '__pycache__/', 'node_modules/', '.next/',
    'venv/', 'env/', '.env/', '.venv/', 'build/', 'dist/', 'site-packages/',
    '.DS_Store', 'Thumbs.db'
]
```

You can disable these defaults with the `--no-defaults` flag.

## Windows Users

When using exclusion patterns on Windows, remember to use forward slashes `/` instead of backslashes `\`:

```bash
python codebase_extractor.py --exclude "temp/" --exclude "logs/"
```

## Performance

The tool is optimized to handle large codebases efficiently:

- Files larger than 10MB are skipped by default (to avoid memory issues)
- Binary files are detected and excluded from content extraction
- Multiple encoding formats are supported (UTF-8, Latin-1, etc.)
- Token counting is optimized to run quickly even on large files

## Large Projects

For very large projects, you can improve performance by:

1. Using selective inclusion to target specific directories
2. Using the progress bar (install `tqdm`) for better visibility
3. Excluding large binary files or data directories

## Use Cases

- **Code Reviews**: Generate a single file with all relevant code for review
- **Documentation**: Include code snippets in technical documentation
- **Onboarding**: Help new team members understand project structure
- **Archiving**: Create text-based snapshots of your codebase
- **AI Tools**: Prepare your codebase for analysis by AI tools or LLMs
  - **Token Optimization**: Include only specific files/folders content to reduce token usage with LLMs
  - **Context Preservation**: Keep the full directory structure for better context awareness
  - **Targeted Analysis**: Focus AI on specific parts of your codebase like one module and its dependencies
  - **Cost Prediction**: Accurately predict token usage costs with OpenAI models

## Limitations

- Basic token counting is used if tiktoken is not installed
- May have issues with very large files (>10MB)
- Binary files are detected but not included in the output

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Made with ❤️ by Adrian and Claude 3.7