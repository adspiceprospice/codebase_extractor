# Codebase Extractor

A simple Python tool to extract and combine code from an entire codebase into a single text file for simplifying workflows when using LLM's. If i get feedback that this is useful, I'll add more features and probably make a free mac app out of it.

# Codebase Extractor

A powerful Python tool to extract and combine code from an entire codebase into a single text file. Perfect for code reviews, documentation, analyzing project structure, or creating a comprehensive view of your project.

## Features

- 📂 **Complete Directory Traversal** - Scans your entire codebase (all directories and subdirectories)
- 🚫 **Customizable Exclusions** - Skip specific file types or directories
- 🌳 **Directory Tree Visualization** - See your project structure at a glance
- 📝 **Token Counting** - Get a rough estimate of the codebase size in tokens
- 🖥️ **Console Feedback** - Visual progress indicators during processing
- ⚙️ **Flexible Configuration** - Command-line arguments for easy customization
- 🛡️ **Safe Extraction** - Prevents recursively indexing previous extraction files
- 📎 **Selective Inclusion** - Include only specified files/folders while maintaining full structure
- 🔄 **Cross-platform** - Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.6 or higher

### Option 1: Clone the repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/codebase_extractor.git
cd codebase_extractor

# Optional: Install dependencies for progress bar
pip install tqdm
```

### Option 2: Download the script directly

You can also download just the `codebase_extractor.py` script and run it directly.

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

This is particularly useful when preparing extracts for AI tools like Large Language Models (LLMs) where you want to:
- Give the AI the complete project structure for context
- Include specific files and entire directories that are relevant to your current task
- Reduce token usage by omitting irrelevant file contents

### Command-line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--root` | `-r` | Root directory to start extraction (default: current directory) |
| `--output` | `-o` | Output file name (default: codebase_extract.txt) |
| `--exclude` | `-e` | Exclude patterns (can be used multiple times) |
| `--include` | `-i` | Only include content for specific files/folders (space or comma separated) |
| `--no-defaults` | | Don't use default exclusions |
| `--no-progress` | | Don't show progress bar |
| `--force` | `-f` | Force overwrite if output file exists (skips confirmation prompt) |

### Exclude Patterns

You can exclude files and directories using patterns:

- `*.ext` - Exclude all files with the extension `.ext`
- `dir_name/` - Exclude directory named `dir_name`
- `filename` - Exclude files named `filename`

### Include Patterns

You can specify which content to include in several ways:

- Individual files:
  - `filename.ext` - Just the filename (will match in any directory)
  - `dir/filename.ext` - Relative path from the root directory
  - `*.py` - Wildcard pattern to include all Python files
  - `models/*.py` - Wildcard pattern to include Python files in a specific directory

- Entire directories:
  - `src/core/` - Include all files in the core directory and its subdirectories
  - `src/core` - Same as above (trailing slash is optional for directories)

## Example Use Case

Imagine you're working on a feature in the `src/core/` module and want to consult an LLM. You can create an extract with:

```bash
python codebase_extractor.py --include "README.md,src/index.ts,src/core/,src/tools/base-tool.ts"
```

This will:
1. Map your entire project structure (for context)
2. Include content from:
   - README.md
   - src/index.ts
   - ALL files in src/core/ and ALL its subdirectories
   - src/tools/base-tool.ts

Perfect for focused AI assistance with minimal token usage!

## Smart Prevention of Self-Indexing

The tool automatically prevents indexing its own output files:

- Automatically excludes the output file from the indexing process
- Detects previous extraction files with the same name
- Prompts for confirmation before overwriting (unless `--force` is used)

This prevents recursive indexing problems and improves overall reliability.

## Example Output

The generated file will have this structure:

```
Total Tokens: 12345

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

All Files (Structure Only):

- README.md
- package.json
- src/index.ts
- src/core/config.ts
- src/core/models/user.ts
- src/core/services/auth.ts
- src/tools/base-tool.ts
- src/tools/specific-tool.ts
- tests/core/user.test.ts

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

## Use Cases

- **Code Reviews**: Generate a single file with all relevant code for review
- **Documentation**: Include code snippets in technical documentation
- **Onboarding**: Help new team members understand project structure
- **Archiving**: Create text-based snapshots of your codebase
- **AI Tools**: Prepare your codebase for analysis by AI tools or LLMs
  - **Token Optimization**: Include only specific files/folders content to reduce token usage with LLMs
  - **Context Preservation**: Keep the full directory structure for better context awareness
  - **Targeted Analysis**: Focus AI on specific parts of your codebase like one module and its dependencies

## Limitations

- Basic token counting (splits on whitespace)
- May have issues with very large files
- Binary files are detected but not included in the output

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Made with ❤️ by Adrian and Claude 3.7