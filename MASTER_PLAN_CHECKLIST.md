Okay, here is the feature request turned into a thorough prompt following your provided `Meta-Structure Definition for Autonomous LLM Execution Prompts v1.2.0 (Unified)` template.

```markdown
Subject: Implement Web Search and URL Scraping Capabilities for LLM

**Date:** 2025-04-14
**Time:** 09:50 UTC-5

## 1. Overall Purpose
This document defines the execution plan for integrating web search and URL scraping functionalities into the target LLM, enabling it to access real-time information and specific web page content autonomously.

## 2. Core Execution Principles & Global Rules
Execution MUST strictly adhere to the **Apex Software Compliance Standards Guide** (`./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md`), proceeding sequentially through Phases, Tasks, and Steps. Each item requires completion, verification against `Internal Success Criteria` (including **all** referenced `[(Rule #X: CODE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-X)`), and marking its checkbox (`- [x]`) before advancing. Verification failures trigger a recursive correction loop. Operation is autonomous; report only upon final completion. All activities must comply with the standards guide, particularly sections on Quality, Security, Testing, and Documentation.

## 3. Mandatory Quality & Finalization Rules (Reference `./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md`)
Continuous enforcement and final verification of **all** applicable rules in the **Apex Software Compliance Standards Guide** (`./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md`) are mandatory, including but not limited to: Code Quality (`QUAL-*`), Line Limits (`QUAL-SIZE`), Configuration (`CONF-*`), Security (`SEC-*`), Testing (`TEST-*`), Documentation (`DOC-*`), Implementation Correctness (`IMPL-*`), and Final Validation (`FINAL-*`, esp. `FINAL-SWEEP`).

## 4. Prompt Template Structure (Section by Section)
* **A. Overall Formatting:** Entire prompt enclosed in ```markdown ... ```. All Phase, Task, Step items begin with `- [ ]`.
* **B. Subject Line:** `Subject: Implement Web Search and URL Scraping Capabilities for LLM`
* **C. Directive Section:** See Section 2 above. Explicit adherence to `./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md` is required. Internal logging per protocol below. No intermediate reporting.
* **D. Test Reporting Protocol (Internal):**
    * **Location:** `docs/Test_Result_Analysis.md`
    * **Format:** Append Markdown table entries: `| Date | Scope | Pass % | Coverage % | Key Findings/Failures |`
    * **Frequency:** Update after each `Task Completion Testing` and `Phase Completion Testing`.
* **E. Hierarchical Execution Blocks:**

---
- [ ] **Phase 1: Setup and Core Framework Definition**
    * **Objective:** Establish the project structure, define core interfaces for search/scraping, and set up initial configuration handling.
    ---
    - [ ] **Task 1.1: Generate/Update Project Structure via Script**
        * **Task Objective:** Define and execute a script to create the necessary project directory structure and essential blank files *based on the established plan*. **If the project root already exists, this script will only ensure the specific folders and files planned for the current execution phase exist, avoiding modification of pre-existing unrelated structures.** If the project root does not exist, it will create the initial full structure.
        - [ ] * **Step 1.1.0 [(Rule #1: PLAN-CHK)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-1):** **Check Project Existence:** Determine if the project root directory already exists.
        - [ ] * **Step 1.1.1 [(Rule #1: PLAN-CHK)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-1), [(Rule #26: CONF-EXT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-26):** **Generate Script Logic:** Create or update a shell script (`scripts/01_setup_project_structure.sh`) or appropriate format.
            * If the project **does not** exist (per Step 1.1.0), the script should contain commands to create **all** necessary top-level and nested directories (e.g., `src/core`, `src/modules/search`, `src/modules/scraping`, `tests/unit`, `tests/integration`, `docs/`, `config/`, `scripts/`) as derived from the *overall* project plan/architecture.
            * If the project **does** exist (per Step 1.1.0), the script should contain commands to create **only** the specific directories required for the *current execution plan* that do not already exist (e.g., `src/modules/search`, `src/modules/scraping` if they are new).
        - [ ] * **Step 1.1.2 [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59), [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56):** **Enhance Script for File Creation:** Modify the script:
            * If the project **does not** exist, it should also create **all** essential blank starter files (e.g., `src/main.js`, `src/core/interface.js`, `src/modules/search/client.js`, `src/modules/scraping/scraper.js`, `README.md`, `docs/architecture.md`, `config/secrets.template.json`, `config/app_config.json`, `scripts/01_setup_project_structure.sh`) within the appropriate directories.
            * If the project **does** exist, it should create **only** the specific blank files required for the *current execution plan* that do not already exist.
            * For *newly created* files (in either case) that support comments (e.g., `.js`, `.py`, `.md`), inject relevant high-level plan comments (e.g., file purpose, related Phase/Task objective). Skip injection for non-commentable types or pre-existing files.
        - [ ] * **Step 1.1.3 [(Rule #26: CONF-EXT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-26):** **Execute:** Run the generated/updated setup script (`scripts/01_setup_project_structure.sh`) to create the necessary directory structure and initial files. Capture any execution errors.
        * **Internal Success Criteria:**
            * The setup script (`scripts/01_setup_project_structure.sh`) is created/updated and contains correct conditional commands for directory and file generation based on project existence.
            * The script executes successfully without errors.
            * The expected directory structure (either full initial or specific additions like `src/modules/search`, `src/modules/scraping`) exists.
            * Essential blank files (either full initial set or specific additions like `search/client.js`, `scraping/scraper.js`) are created correctly, avoiding overwrites.
            * Newly created commentable files contain injected plan-related comments.
            * Compliance with all referenced Apex Standards Rules [(Rule #1: PLAN-CHK)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-1), [(Rule #26: CONF-EXT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-26), [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59), [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56).
        * **Internal Verification Method:**
            * Review the generated script content (`scripts/01_setup_project_structure.sh`) for correctness and conditional logic against the plan and project existence state.
            * Verify script execution completed successfully (exit code 0) and check logs for errors.
            * List the directory structure (`ls -R`) and verify it matches the script's intent.
            * Check for the existence and content (initial comments) of the specified blank files using file system commands.
            * Verify compliance with referenced Apex Standards Rules for this Task and its Steps.
        * **Task Completion Testing (Internal):** N/A (Setup Task). Update internal development log `docs/Test_Result_Analysis.md` noting successful setup.
    ---
    - [ ] **Task 1.2: Define Core Interfaces and Data Structures**
        * **Task Objective:** Define abstract interfaces or base classes for search and scraping modules, along with common data structures for inputs and outputs.
        - [ ] * **Step 1.2.1 [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14):** **Define Search Interface:** In `src/core/interface.js` (or equivalent), define an abstract class or interface (`SearchProvider`) with methods like `search(query: string): Promise<SearchResult[]>`.
        - [ ] * **Step 1.2.2 [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14):** **Define Scraping Interface:** In `src/core/interface.js`, define an abstract class or interface (`ScrapingProvider`) with methods like `scrape(url: string, desired_content: string[]): Promise<ScrapedData>`.
        - [ ] * **Step 1.2.3 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Define Data Structures:** Define clear data structures/types for `SearchResult` (e.g., title, snippet, url) and `ScrapedData` (e.g., extracted_text, tables, metadata). Place these definitions appropriately (e.g., within `src/core/types.js` or alongside interfaces).
        - [ ] * **Step 1.2.4 [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56):** **Document Interfaces:** Add documentation comments (e.g., JSDoc) explaining the purpose and usage of the interfaces and data structures.
        * **Internal Success Criteria:**
            * `src/core/interface.js` (or equivalent) contains well-defined interfaces/classes for `SearchProvider` and `ScrapingProvider`.
            * Common data structures (`SearchResult`, `ScrapedData`) are clearly defined.
            * Interfaces and structures are documented appropriately.
            * Compliance with referenced Apex Standards Rules [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14), [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8), [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56).
        * **Internal Verification Method:**
            * Review the code in `src/core/interface.js` and related files for correctness, clarity, and adherence to defined structures.
            * Check documentation comments for completeness.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Interface Definition). Update log.
    ---
    - [ ] **Task 1.3: Setup Configuration Management**
        * **Task Objective:** Implement loading and validation of configuration, including placeholders for API keys.
        - [ ] * **Step 1.3.1 [(Rule #25: CONF-LOAD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-25):** **Implement Config Loader:** Create a utility (e.g., `src/core/config_loader.js`) to load settings from `config/app_config.json`.
        - [ ] * **Step 1.3.2 [(Rule #27: CONF-SENS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-27), [(Rule #33: SEC-KEY)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-33):** **Handle Secrets:** Ensure the config loader can merge or prioritize secrets (like API keys) from environment variables or a separate `.env` / `config/secrets.json` file (using `config/secrets.template.json` as a template). Do *not* commit actual secrets.
        - [ ] * **Step 1.3.3 [(Rule #28: CONF-VAL)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-28):** **Add Validation:** Implement basic validation to ensure required configuration keys (e.g., placeholder for search API key) are present upon loading.
        * **Internal Success Criteria:**
            * Configuration loader exists and functions correctly.
            * Mechanism for handling secrets externally is implemented.
            * Basic configuration validation is performed.
            * No secrets are hardcoded or committed.
            * Compliance with referenced Apex Standards Rules [(Rule #25: CONF-LOAD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-25), [(Rule #27: CONF-SENS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-27), [(Rule #33: SEC-KEY)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-33), [(Rule #28: CONF-VAL)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-28).
        * **Internal Verification Method:**
            * Review the config loader code.
            * Test loading with sample config and secrets files/env vars.
            * Test validation logic by providing incomplete configurations.
            * Check git history/status to ensure no secrets were committed.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Create simple unit tests for the config loader (`tests/unit/test_config_loader.js`). Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Phase Completion Testing (Internal)**
        - [ ] * **Step 1.P1:** **Review Phase Artifacts:** Check that all files created/modified in Phase 1 adhere to coding standards and structure.
        - [ ] * **Step 1.P2:** **Run Phase 1 Tests:** Execute all unit tests created in this phase (config loader tests).
        - [ ] * **Step 1.P3:** **Update Log:** Record Phase 1 completion status and test results in `docs/Test_Result_Analysis.md`.
---
- [ ] **Phase 2: Web Search Implementation**
    * **Objective:** Implement the web search functionality using an external API and integrate it with the core framework.
    ---
    - [ ] **Task 2.1: Integrate Search API Client**
        * **Task Objective:** Set up and configure the client library for the chosen search API (e.g., SerpAPI or Google Custom Search).
        - [ ] * **Step 2.1.1 [(Rule #N/A: DEV-CHOICE)]: **Choose Search API:** Select a suitable search API (e.g., SerpAPI, Google Custom Search API). Document rationale briefly in `docs/architecture.md`. *Defaulting to SerpAPI for this plan unless overridden.*
        - [ ] * **Step 2.1.2 [(Rule #2: PLAN-DEPS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-2):** **Add Dependency:** Add the necessary client library (e.g., `google-search-results-nodejs` for SerpAPI) to project dependencies.
        - [ ] * **Step 2.1.3 [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #33: SEC-KEY)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-33):** **Implement Client Wrapper:** In `src/modules/search/client.js`, create a wrapper class/function that initializes the API client using the API key loaded via the configuration manager (Task 1.3). Ensure it adheres to the `SearchProvider` interface (Task 1.2).
        - [ ] * **Step 2.1.4 [(Rule #40: SEC-INPUT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-40):** **Basic Input Sanitization:** Add basic checks or sanitization for the search query input if the API requires it.
        * **Internal Success Criteria:**
            * Search API client library is added as a dependency.
            * A wrapper in `src/modules/search/client.js` initializes the client using configuration.
            * The wrapper conforms to the `SearchProvider` interface.
            * API key handling is secure (uses config loader).
            * Basic input checks are present.
            * Compliance with referenced Apex Standards Rules [(Rule #2: PLAN-DEPS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-2), [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #33: SEC-KEY)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-33), [(Rule #40: SEC-INPUT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-40).
        * **Internal Verification Method:**
            * Review code in `src/modules/search/client.js`.
            * Check dependency files (e.g., `package.json`).
            * Verify API key is not hardcoded.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Implementation focus). Update log.
    ---
    - [ ] **Task 2.2: Implement Search Execution Logic**
        * **Task Objective:** Implement the logic to perform a search query using the API client and handle potential API errors.
        - [ ] * **Step 2.2.1 [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7):** **Implement `search` Method:** Implement the `search(query)` method in the `src/modules/search/client.js` wrapper. This method should call the underlying search API client with the provided query.
        - [ ] * **Step 2.2.2 [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21):** **Implement API Error Handling:** Add try/catch blocks and error handling logic to manage potential issues during the API call (e.g., network errors, invalid API key, rate limits). Log errors appropriately.
        * **Internal Success Criteria:**
            * The `search` method correctly calls the search API.
            * API errors are handled gracefully (e.g., return empty results or throw specific exceptions).
            * Errors are logged according to standards.
            * Compliance with referenced Apex Standards Rules [(Rule #7: QUAL-API)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-7), [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21).
        * **Internal Verification Method:**
            * Review the `search` method implementation.
            * Check error handling paths.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Add unit tests (`tests/unit/test_search_client.js`) mocking the API client to test the search execution logic and error handling. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Task 2.3: Implement Result Processing**
        * **Task Objective:** Process the raw results from the search API into the standardized `SearchResult` format.
        - [ ] * **Step 2.3.1 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Map API Response:** Modify the `search` method to parse the raw API response.
        - [ ] * **Step 2.3.2 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8), [(Rule #58: IMPL-SUMM)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-58):** **Extract Relevant Fields:** Extract relevant fields (e.g., title, URL, snippet/summary) from each result in the API response.
        - [ ] * **Step 2.3.3 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Format as `SearchResult[]`:** Format the extracted data into an array of `SearchResult` objects, conforming to the structure defined in Task 1.2. Return this array. Consider limiting the number of results returned (e.g., top 5).
        * **Internal Success Criteria:**
            * The `search` method returns an array of `SearchResult` objects.
            * Data is correctly extracted and mapped from the API response to the standard format.
            * The number of results is managed appropriately.
            * Compliance with referenced Apex Standards Rules [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8), [(Rule #58: IMPL-SUMM)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-58).
        * **Internal Verification Method:**
            * Review the result processing logic within the `search` method.
            * Use sample API responses (real or mocked) to verify the mapping and formatting.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Extend unit tests (`tests/unit/test_search_client.js`) to cover result processing using mock API responses. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Phase Completion Testing (Internal)**
        - [ ] * **Step 2.P1:** **Review Phase Artifacts:** Check `src/modules/search/client.js` and related test files for standards compliance.
        - [ ] * **Step 2.P2:** **Run Phase 2 Tests:** Execute all unit tests for the search module (`tests/unit/test_search_client.js`).
        - [ ] * **Step 2.P3:** **(Optional) Live API Test:** If feasible and configured, perform a single live API call with a test query to ensure end-to-end function (requires API key setup). Log outcome.
        - [ ] * **Step 2.P4:** **Update Log:** Record Phase 2 completion status and test results in `docs/Test_Result_Analysis.md`.
---
- [ ] **Phase 3: URL Scraping Implementation**
    * **Objective:** Implement the URL scraping functionality using appropriate libraries and integrate it with the core framework.
    ---
    - [ ] **Task 3.1: Select and Integrate Scraping Library**
        * **Task Objective:** Choose and add libraries for fetching and parsing HTML content.
        - [ ] * **Step 3.1.1 [(Rule #N/A: DEV-CHOICE)]: **Choose Libraries:** Select libraries for HTTP requests (e.g., `axios`, `node-fetch`) and HTML parsing (e.g., `cheerio`, `jsdom`). Document rationale briefly in `docs/architecture.md`. *Defaulting to `axios` and `cheerio` for this plan.*
        - [ ] * **Step 3.1.2 [(Rule #2: PLAN-DEPS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-2):** **Add Dependencies:** Add the chosen libraries to project dependencies.
        - [ ] * **Step 3.1.3 [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14):** **Implement Scraper Wrapper:** In `src/modules/scraping/scraper.js`, create a class/function that will house the scraping logic and conform to the `ScrapingProvider` interface (Task 1.2).
        * **Internal Success Criteria:**
            * HTTP request and HTML parsing libraries are added as dependencies.
            * A wrapper structure exists in `src/modules/scraping/scraper.js` conforming to the `ScrapingProvider` interface.
            * Compliance with referenced Apex Standards Rules [(Rule #2: PLAN-DEPS)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-2), [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14).
        * **Internal Verification Method:**
            * Review code structure in `src/modules/scraping/scraper.js`.
            * Check dependency files.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Implementation focus). Update log.
    ---
    - [ ] **Task 3.2: Implement URL Fetching Logic**
        * **Task Objective:** Implement the logic to fetch HTML content from a given URL, handling potential errors.
        - [ ] * **Step 3.2.1 [(Rule #40: SEC-INPUT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-40):** **Validate URL Input:** Implement validation within the `scrape` method in `src/modules/scraping/scraper.js` to ensure the input is a valid HTTP/HTTPS URL.
        - [ ] * **Step 3.2.2 [(Rule #39: SEC-SRF)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-39):** **Implement Fetching:** Use the chosen HTTP library (e.g., `axios`) to make a GET request to the validated URL. Set appropriate headers (e.g., User-Agent) to mimic a browser and potentially avoid blocking. Consider timeouts.
        - [ ] * **Step 3.2.3 [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21):** **Implement Fetch Error Handling:** Add try/catch blocks to handle network errors, invalid URLs (post-validation fetch failure), non-successful HTTP status codes (e.g., 404, 500), and timeouts. Log errors. Return appropriate error indication or throw specific exceptions.
        * **Internal Success Criteria:**
            * URL input is validated.
            * HTML content is fetched using the HTTP library with appropriate headers/timeouts.
            * Fetching errors (network, HTTP status, timeouts) are handled gracefully and logged.
            * Compliance with referenced Apex Standards Rules [(Rule #40: SEC-INPUT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-40), [(Rule #39: SEC-SRF)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-39), [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21).
        * **Internal Verification Method:**
            * Review the fetching logic and error handling in `src/modules/scraping/scraper.js`.
            * Test with valid and invalid URLs (mocking the HTTP request).
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Add unit tests (`tests/unit/test_scraper.js`) mocking the HTTP library to test URL validation, fetching, and error handling. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Task 3.3: Implement Content Extraction Logic**
        * **Task Objective:** Parse the fetched HTML and extract requested content types (text, tables, metadata).
        - [ ] * **Step 3.3.1 [(Rule #N/A: IMPL-PARSE)]: **Parse HTML:** Use the chosen parsing library (e.g., `cheerio`) to load the fetched HTML content.
        - [ ] * **Step 3.3.2 [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59):** **Implement Text Extraction:** Add logic to extract the main textual content, possibly by targeting common tags (`p`, `article`, `main`) or using heuristics to remove boilerplate (nav, footer). Handle cases where extraction fails.
        - [ ] * **Step 3.3.3 [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59):** **Implement Table Extraction:** Add logic to find `<table>` elements and extract their data into a structured format (e.g., array of arrays). Handle cases where no tables are found.
        - [ ] * **Step 3.3.4 [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59):** **Implement Metadata Extraction:** Add logic to extract common metadata (e.g., `<title>`, `<meta description>`). Handle cases where metadata is missing.
        - [ ] * **Step 3.3.5 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Filter by Request:** Use the `desired_content` parameter (from the interface) to determine which types of content (text, tables, metadata) should be extracted and returned in the `ScrapedData` object.
        - [ ] * **Step 3.3.6 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Format as `ScrapedData`:** Populate and return the `ScrapedData` object (defined in Task 1.2) with the extracted content.
        * **Internal Success Criteria:**
            * Fetched HTML is parsed correctly.
            * Logic exists to extract text, tables, and metadata.
            * Extraction handles missing elements gracefully.
            * Extraction respects the `desired_content` input parameter.
            * Results are returned in the standardized `ScrapedData` format.
            * Compliance with referenced Apex Standards Rules [(Rule #59: IMPL-PLACE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-59), [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8).
        * **Internal Verification Method:**
            * Review the parsing and extraction logic in `src/modules/scraping/scraper.js`.
            * Test with sample HTML snippets containing text, tables, and metadata, verifying correct extraction and formatting into `ScrapedData`.
            * Test the filtering based on `desired_content`.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Extend unit tests (`tests/unit/test_scraper.js`) to cover content extraction using mock HTML content. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Phase Completion Testing (Internal)**
        - [ ] * **Step 3.P1:** **Review Phase Artifacts:** Check `src/modules/scraping/scraper.js` and related test files for standards compliance.
        - [ ] * **Step 3.P2:** **Run Phase 3 Tests:** Execute all unit tests for the scraping module (`tests/unit/test_scraper.js`).
        - [ ] * **Step 3.P3:** **(Optional) Live Scrape Test:** If feasible, attempt to scrape a simple, permissive test webpage to verify end-to-end function. Log outcome.
        - [ ] * **Step 3.P4:** **Update Log:** Record Phase 3 completion status and test results in `docs/Test_Result_Analysis.md`.
---
- [ ] **Phase 4: Integration and Control Logic**
    * **Objective:** Integrate the search and scraping modules into the main LLM flow, allowing the LLM to decide when and how to use them based on user input.
    ---
    - [ ] **Task 4.1: Develop Input Parser/Detector**
        * **Task Objective:** Create logic to analyze LLM input prompts to detect requests for web searches or URL scrapes, and extract necessary parameters (query, URL).
        - [ ] * **Step 4.1.1 [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14):** **Create Parser Module:** Create a new module/utility (e.g., `src/core/input_parser.js`).
        - [ ] * **Step 4.1.2 [(Rule #60: IMPL-REGEX)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-60):** **Implement URL Detection:** Add logic (e.g., using regular expressions) to identify URLs within the input text.
        - [ ] * **Step 4.1.3 [(Rule #60: IMPL-REGEX)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-60):** **Implement Search Keyword Detection:** Add logic to detect keywords or patterns indicating a general search request (e.g., "search for...", "what is the latest on...").
        - [ ] * **Step 4.1.4 [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8):** **Define Output Structure:** Define a structure returned by the parser indicating the detected action (search, scrape, none) and extracted parameters (query, url, desired_content).
        * **Internal Success Criteria:**
            * Input parser module exists.
            * URLs are reliably detected in input text.
            * Search intent keywords/patterns are detected.
            * Parser returns a clear structure indicating action and parameters.
            * Compliance with referenced Apex Standards Rules [(Rule #14: QUAL-MOD)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-14), [(Rule #60: IMPL-REGEX)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-60), [(Rule #8: QUAL-DATA)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-8).
        * **Internal Verification Method:**
            * Review the parser logic.
            * Test with various input strings containing URLs, search terms, and neither.
            * Verify the output structure is correct.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Create unit tests (`tests/unit/test_input_parser.js`) for the parser logic. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Task 4.2: Integrate Modules into Main LLM Logic**
        * **Task Objective:** Modify the main LLM processing flow to use the input parser and invoke the search or scraping modules when detected.
        - [ ] * **Step 4.2.1 [(Rule #15: QUAL-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-15):** **Modify Main Flow:** Identify the point in the LLM's request processing logic where external tool use can be triggered.
        - [ ] * **Step 4.2.2 [(Rule #15: QUAL-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-15):** **Invoke Parser:** Call the input parser (Task 4.1) with the user's prompt.
        - [ ] * **Step 4.2.3 [(Rule #15: QUAL-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-15):** **Conditional Invocation:** Based on the parser's output, conditionally instantiate and call the appropriate provider (`SearchProvider` or `ScrapingProvider`) using the extracted parameters.
        - [ ] * **Step 4.2.4 [(Rule #15: QUAL-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-15):** **Incorporate Results:** Integrate the results (`SearchResult[]` or `ScrapedData`) back into the LLM's context or use them to formulate the final response.
        * **Internal Success Criteria:**
            * Main LLM logic calls the input parser.
            * Search or scraping modules are invoked conditionally based on parser output.
            * Results from the modules are accessible/used by the LLM.
            * Integration points are clearly defined and follow modular design.
            * Compliance with referenced Apex Standards Rules [(Rule #15: QUAL-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-15).
        * **Internal Verification Method:**
            * Review the modified LLM processing code.
            * Trace the flow for inputs requiring search, scraping, or neither.
            * Verify correct module invocation and result handling.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Create integration tests (`tests/integration/test_llm_integration.js`) that simulate LLM calls with different inputs and verify the correct module (search/scrape/none) is triggered (mocking the actual module execution). Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Task 4.3: Implement Error Handling at Integration Level**
        * **Task Objective:** Add error handling around the module calls within the main LLM flow.
        - [ ] * **Step 4.3.1 [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21):** **Handle Module Errors:** Wrap the calls to the search and scraping modules in try/catch blocks within the main LLM logic.
        - [ ] * **Step 4.3.2 [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21):** **Inform User:** If a search or scrape fails (e.g., invalid URL, API error, scraping blocked), ensure the LLM can inform the user gracefully (e.g., "I couldn't retrieve information from that source because...") instead of crashing.
        - [ ] * **Step 4.3.3 [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21):** **Log Integration Errors:** Log errors encountered during the integration step (e.g., failure to instantiate a module, unexpected error from a module).
        * **Internal Success Criteria:**
            * Errors from search/scraping modules are caught by the main LLM logic.
            * Failures result in graceful degradation or user notification, not application crashes.
            * Integration-level errors are logged.
            * Compliance with referenced Apex Standards Rules [(Rule #21: QUAL-ERR)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-21).
        * **Internal Verification Method:**
            * Review error handling code in the main LLM flow.
            * Test integration points by forcing mocked modules to throw errors and observe LLM behavior.
            * Check logs for appropriate error messages.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Extend integration tests (`tests/integration/test_llm_integration.js`) to cover error scenarios where mocked search/scrape modules fail. Update `docs/Test_Result_Analysis.md`.
    ---
    - [ ] **Phase Completion Testing (Internal)**
        - [ ] * **Step 4.P1:** **Review Phase Artifacts:** Check integration code (`src/core/input_parser.js`, modified main LLM logic) and related test files for standards compliance.
        - [ ] * **Step 4.P2:** **Run Phase 4 Tests:** Execute all unit tests (`test_input_parser.js`) and integration tests (`test_llm_integration.js`) created in this phase.
        - [ ] * **Step 4.P3:** **Update Log:** Record Phase 4 completion status and test results in `docs/Test_Result_Analysis.md`.
---
- [ ] **Phase 5: Documentation and Finalization**
    * **Objective:** Complete documentation, perform final testing, and ensure overall quality and compliance.
    ---
    - [ ] **Task 5.1: Update/Create User Documentation**
        * **Task Objective:** Document the new web search and URL scraping capabilities for end-users.
        - [ ] * **Step 5.1.1 [(Rule #50: DOC-USER)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-50):** **Explain Functionality:** Describe how users can trigger web searches (e.g., using specific phrasing) and URL scrapes (by including a URL).
        - [ ] * **Step 5.1.2 [(Rule #50: DOC-USER)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-50):** **Provide Examples:** Include clear examples of input prompts for both searching and scraping.
        - [ ] * **Step 5.1.3 [(Rule #50: DOC-USER)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-50):** **Mention Limitations:** Briefly mention potential limitations (e.g., inability to scrape certain sites, potential for outdated search results).
        - [ ] * **Step 5.1.4 [(Rule #50: DOC-USER)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-50):** **Update README/User Guide:** Integrate this information into the main `README.md` or user guide document.
        * **Internal Success Criteria:**
            * User documentation accurately reflects the new features.
            * Examples are clear and helpful.
            * Limitations are noted.
            * Documentation is integrated into the project's standard user docs.
            * Compliance with referenced Apex Standards Rules [(Rule #50: DOC-USER)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-50).
        * **Internal Verification Method:**
            * Review the user documentation content for clarity, accuracy, and completeness.
            * Verify examples work as described (conceptually).
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Documentation Task). Update log.
    ---
    - [ ] **Task 5.2: Update/Create Developer Documentation**
        * **Task Objective:** Document the implementation details for developers.
        - [ ] * **Step 5.2.1 [(Rule #51: DOC-DEV)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-51), [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56):** **Document Modules:** Add/update documentation comments (e.g., JSDoc) within the code for all new/modified modules (`search`, `scraping`, `input_parser`, core interfaces, config loader).
        - [ ] * **Step 5.2.2 [(Rule #51: DOC-DEV)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-51):** **Update Architecture Document:** Update `docs/architecture.md` to include the new modules, their interactions, chosen external APIs/libraries, and design decisions.
        - [ ] * **Step 5.2.3 [(Rule #51: DOC-DEV)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-51):** **Explain Configuration:** Detail the required configuration settings (API keys, etc.) in the developer documentation or README.
        * **Internal Success Criteria:**
            * Code includes comprehensive documentation comments.
            * Architecture document is updated to reflect the new components.
            * Configuration requirements are clearly documented for developers.
            * Compliance with referenced Apex Standards Rules [(Rule #51: DOC-DEV)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-51), [(Rule #56: DOC-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-56).
        * **Internal Verification Method:**
            * Review code comments for completeness and accuracy.
            * Review `docs/architecture.md` and other developer documentation.
            * Verify configuration documentation matches implementation.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Documentation Task). Update log.
    ---
    - [ ] **Task 5.3: Comprehensive Testing and Refinement**
        * **Task Objective:** Perform end-to-end testing and refine implementation based on results.
        - [ ] * **Step 5.3.1 [(Rule #45: TEST-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-45):** **Execute All Tests:** Run the complete test suite (unit and integration tests). Ensure all pass.
        - [ ] * **Step 5.3.2 [(Rule #46: TEST-E2E)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-46):** **Manual End-to-End Testing:** Perform manual tests using sample prompts covering:
            * General web search requests.
            * URL scraping requests (use test-friendly URLs).
            * Inputs that should trigger neither.
            * Edge cases (invalid URLs, complex queries, sites likely to block scraping).
        - [ ] * **Step 5.3.3 [(Rule #13: QUAL-PERF)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-13):** **Assess Performance:** Briefly assess the response time impact when search/scraping is triggered. Note any significant delays.
        - [ ] * **Step 5.3.4 [(Rule #N/A: IMPL-REFINE)]: **Refine Implementation:** Based on test results and performance assessment, make necessary code adjustments or refinements. Re-run relevant tests after changes.
        * **Internal Success Criteria:**
            * All automated tests pass.
            * Manual end-to-end tests confirm functionality works as expected for primary use cases.
            * Error handling behaves correctly during manual tests.
            * Performance impact is acceptable.
            * Necessary refinements are implemented and tested.
            * Compliance with referenced Apex Standards Rules [(Rule #45: TEST-INT)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-45), [(Rule #46: TEST-E2E)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-46), [(Rule #13: QUAL-PERF)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-13).
        * **Internal Verification Method:**
            * Check test runner output for passing status.
            * Review manual test case results documentation (can be informal notes or added to `docs/Test_Result_Analysis.md`).
            * Evaluate performance observations.
            * Review any code changes made during refinement.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** Update `docs/Test_Result_Analysis.md` with final comprehensive test results, including manual test outcomes and performance notes.
    ---
    - [ ] **Task 5.4: Final Code Review and Standards Sweep**
        * **Task Objective:** Perform a final review of all code and artifacts against the Apex Standards.
        - [ ] * **Step 5.4.1 [(Rule #63: FINAL-SWEEP)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-63):** **Code Review:** Conduct a thorough self-review of all new and modified code introduced for this feature.
        - [ ] * **Step 5.4.2 [(Rule #63: FINAL-SWEEP)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-63):** **Standards Compliance Check:** Explicitly verify adherence to **all** relevant rules in `./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md`, including code style, naming, comments, error handling, security, configuration, testing, and documentation.
        - [ ] * **Step 5.4.3 [(Rule #63: FINAL-SWEEP)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-63):** **Dependency Check:** Ensure only necessary dependencies were added and that they are documented.
        - [ ] * **Step 5.4.4 [(Rule #63: FINAL-SWEEP)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-63):** **Clean Up:** Remove any temporary files, commented-out dead code, or unnecessary logs.
        * **Internal Success Criteria:**
            * All code meets quality and style guidelines.
            * Full compliance with the Apex Standards Guide is confirmed.
            * Dependencies are correct and justified.
            * Codebase is clean and free of artifacts from development.
            * Compliance with referenced Apex Standards Rules [(Rule #63: FINAL-SWEEP)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-63).
        * **Internal Verification Method:**
            * Manually inspect code and documentation against the standards guide checklist (implicitly derived from the guide).
            * Use linters or static analysis tools if configured for the project.
            * Review project dependencies.
            * Verify compliance with referenced Apex Standards Rules.
        * **Task Completion Testing (Internal):** N/A (Final Review Task). Update log confirming successful completion of the final sweep.
    ---
    - [ ] **Phase Completion Testing (Internal)**
        - [ ] * **Step 5.P1:** **Final Verification:** Confirm all previous phase and task checkboxes are marked complete (`- [x]`).
        - [ ] * **Step 5.P2:** **Run Final Test Suite:** Execute the entire test suite one last time.
        - [ ] * **Step 5.P3:** **Review Final Log:** Check `docs/Test_Result_Analysis.md` for completeness and overall success.
        - [ ] * **Step 5.P4:** **Update Log:** Add final entry indicating Phase 5 completion and overall project success to `docs/Test_Result_Analysis.md`.

* **F. Final Instruction:**
    Begin execution of this plan. Adhere strictly to the sequential processing of Phases, Tasks, and Steps, marking checkboxes `- [x]` only upon successful completion and verification against Internal Success Criteria, including **all** linked `[(Rule #X: CODE)](./STANDARDS_REPOSITORY/apex/APEX_STANDARDS.md#rule-X)` requirements from the **Apex Software Compliance Standards Guide**. Verification failures MUST trigger the recursive error handling/retry logic. Perform the final standards sweep (`Task 5.4`) and ensure all tasks are complete before concluding. Report ONLY upon successful completion of all phases.

* **G. Contextual Footer:**
    *(Instructions generated: 2025-04-14 09:50 UTC-5. Location context: Menasha, Wisconsin, United States)*
```