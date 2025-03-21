# README


### **Workflow Dependency - Pipeline Execution Chain**
- **Data Initialisation:**
  - Uses DataModuleHandler to retrieve DataModules
  - Data modules stored in a dictionary
  - Supports LazyLoading through the StepDefinitions
- **Step Resolution:**
  - StepHandler retrieves StepDefinitions from ``src/pipelines/steps/*_steps.py``
  - Converts to StepDefinition objects
- **Execution Orchestration:**
  - StepFactory receives mapped StepDefinitions
  - Runs steps in order using `run_pipeline()` for complex flows with checkpoints
  - Runs steps in order using `run_main()` for linear executions (`main.py`)
- **Step Registration:**
  - Steps are declared in ``src/pipeline/steps/*_steps.py`` using decorators
  - Metadata is preserved in ``steps_metadata.json`` for debugging and visibility

**Workflow Result**:
1. **Loose Coupling:** Components interact through well-defined interfaces
2. **Late Binding:** Data loading deffered until step execution
3. **Discovery:** All steps visible via `StepRegistry.list_all_steps()`
4. **Reusability:** Step definitions shared across pipelines via registry

```mermaid
sequenceDiagram
    participant Main
    participant Pipeline
    participant StepHandler
    participant StepRegistry
    participant StepDefinition
    participant StepFactory
    participant DataModuleHandler
    participant DataModule
    participant LazyLoad
    participant StepInstance
    participant StepMethod

    Main ->> Pipeline: Execute validate_names()
    Pipeline ->> StepHandler: get_step_defs("validation")

    StepHandler ->> StepRegistry: Query registered steps
    StepRegistry -->> StepHandler: Return @register metadata
    StepHandler ->> StepFactory: create_step_map()
    StepFactory ->> StepRegistry: List all registered steps
    StepRegistry -->> StepFactory: Return step metadata
    StepFactory ->> StepDefinition: Create step instances

    Pipeline ->> DataModuleHandler: get_dm(raw-data)
    DataModuleHandler ->> DataModule: Create / Retrieve Data
    DataModuleHandler ->> LazyLoad: Resolve LazyLoad
    LazyLoad ->> DataModule: load()

    StepFactory ->> StepInstance: Instantiate with resolved args
    StepInstance ->> StepMethod: Execute with logging
    StepMethod -->> Pipeline: Return execution result
```

```mermaid
graph TD
    subgraph Core_Base["Core - Base"]
        PC[PipelineContext]
        BP[BasePipeline]
    end

    subgraph Core_Step["Core - Step Handling"]
        SH[StepHandler]
        SF[StepFactory]
        SR[StepRegistry]
        STDef[StepDefinition]
    end

    subgraph Core_Data["Core - Data Handling"]
        DMH[DataModuleHandler]
        DM[DataModule]
        LL[LazyLoad]
    end

    style Core_Base fill:#ffd8b1,stroke:#111
    style Core_Step fill:#2222,stroke:#111
    style Core_Data fill:#6123,stroke:#111
```

```mermaid
graph LR
    MainPipeline -->|Calls| BasePipeline
    BasePipeline -->|Calls| DataModuleHandler
    BasePipeline -->|Uses| StepFactory
    DataModuleHandler -->|Manages| DataModule
    DataModule -->|Supports| LazyLoad
    StepFactory -->|Calls| StepHandler
    StepHandler -->|Queries| StepRegistry
    StepRegistry -->|Stores| StepDefinition
```

![framework classDiagram](reports/framework_classDiagram.png)
