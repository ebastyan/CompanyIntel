# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a data repository containing Excel (.xlsx) files related to waste collection and metal materials management. The files appear to be from a Romanian waste management system dated from January 2023.

## File Structure

### Main Database
- `colectare deseuri punct ro DUMP 2023.xlsx` - Main waste collection database (2023 dump)

### Material Categories
- `aluminiu.xlsx` - Aluminum materials data
- `metale.xlsx` - General metals data
- `neferoase.xlsx` - Non-ferrous metals data
- `q_inox.xlsx` - Stainless steel (inox) data
- `q_importator_profile_aluminiu.xlsx` - Aluminum profile importer data

### Numbered Series Files
- Files numbered 2442-2445, 3811-3812, 3821, 3831-3832, 4677 - These appear to be specific dataset identifiers or batch codes

## Working with Excel Files

Since this repository contains only Excel data files, any data processing or analysis will require:
- Excel file reading capabilities (e.g., pandas, openpyxl for Python)
- Understanding of Romanian terminology for waste/metal categories
- Careful handling of data encoding (files may contain Romanian diacritics)

## Data Context

The data appears to be from a waste collection and metal recycling management system, with focus on:
- Various metal types (aluminum, stainless steel, non-ferrous)
- Waste collection points
- Import profiles for aluminum materials

## AI Team Configuration

This data-centric repository has been configured with a specialized AI team optimized for data analysis, machine learning, and Python development tasks. The following agents have been selected based on the repository's focus on Excel data processing and potential analysis needs:

### Core Team (Primary Specialists)

**ml-data-expert** - Primary data science specialist
- **Expertise**: Machine Learning, Data Science, statistical analysis, data visualization
- **Use cases**:
  - Excel file processing and analysis
  - Pattern recognition in waste collection data
  - Predictive modeling for metal recycling trends
  - Data visualization and reporting
  - Statistical analysis of Romanian waste management data
- **Technologies**: scikit-learn, TensorFlow, PyTorch, pandas, numpy, matplotlib, seaborn

**python-expert** - Core development specialist
- **Expertise**: Modern Python 3.12+, data processing pipelines, automation
- **Use cases**:
  - Building data processing scripts
  - Creating ETL pipelines for Excel data
  - Automation of data cleaning and transformation
  - API development for data access
  - Integration with database systems
- **Technologies**: FastAPI, pandas, SQLAlchemy, asyncio, Pydantic

**documentation-specialist** - Technical documentation
- **Expertise**: Creating clear technical documentation, user guides, API specs
- **Use cases**:
  - Documenting data schemas and field meanings
  - Creating analysis reports and findings
  - User guides for data processing scripts
  - Technical specifications for data workflows

### Supporting Team (Secondary Specialists)

**project-analyst** - Technology stack analysis
- **Expertise**: Rapid technology detection, architecture analysis
- **Use cases**:
  - Analyzing data structure and formats
  - Recommending optimal technology stack
  - Identifying patterns in data organization

### Routing Rules

For any data analysis or processing tasks in this repository:

1. **Start with ml-data-expert** for:
   - Data exploration and analysis
   - Statistical modeling
   - Machine learning applications
   - Data visualization needs
   - Pattern recognition tasks

2. **Use python-expert** for:
   - Building data processing infrastructure
   - Creating automation scripts
   - API development
   - Database integration
   - Performance optimization

3. **Use documentation-specialist** for:
   - Documenting findings and insights
   - Creating user-friendly reports
   - Explaining Romanian terminology and data context
   - Technical documentation

4. **Use project-analyst** when:
   - Exploring new data sources
   - Analyzing data structure patterns
   - Recommending technology approaches

### Team Workflow

1. **Data Analysis Tasks**: ml-data-expert → python-expert (if infrastructure needed) → documentation-specialist
2. **Infrastructure Development**: python-expert → documentation-specialist
3. **Exploratory Tasks**: project-analyst → ml-data-expert → documentation-specialist
4. **Reporting Tasks**: ml-data-expert → documentation-specialist

This configuration ensures optimal handling of Excel-based waste management data with expertise in Romanian language context and metal recycling domain knowledge.