# Adonis
- An Instrumentation-Free and Hardware-Independent Control Flow Recovery Tool
- This repository is based on a fork of [EOSAFE](https://www.usenix.org/conference/usenixsecurity21/presentation/he-ningyu), a symbolic execution engine for WebAssembly (Wasm)

## Introduction

*Adonis* is able to recover the control flow of a failed execution based on the OS-level traces, including dynamic library functions and system call traces. *Adonis* has moderate runtime, development, and deployment cost thus is suitable for the control flow recovery task in production environments.

*Adonis* is easy to use by taking the following two steps:

- Monitor the dynamic library functions or system calls.
- Analyze the control flow of the execution based on the trace collected by the previous step.

Bellow is an example:

```
example/run_example.sh
```

## Project Structure

```
root:
|-- adonis_res: resources and caches used by Adonis during analysis
|-- example: an end-to-end example
|-- hooking: code related to automatically generating proxy library to monitor dynamic function traces
|-- octopus: code related to OS-level traces analysis
|-- paper_experiments: benchmarks and scripts used in our paper
|-- adonis.py: entrance of Adonis
|-- gvar.py: gvar module
```

For details, we leave a README file (if necessary) in each folder.

## Build and Test

Get *Adonis* and run an end-to-end example.

```shell
git clone https://github.com/AsplosSubmission/Adonis
cd Adonis
pip install -r requirements.txt
example/run_example.sh
```

For paper experiments, please see more details in paper_experiments folder.

## Change Log

### 2022.09.08

- Add `sqlite3` application to `paper_experiments` dir, our evaluation results can be found at `paper_experiments/app/sqlite/sqlite_eva_result.json`.
- Improve the initialization speed, including coverage information calculation speed and format string extraction speed.
- Solve several bugs that would result in infinite loop.

## Notes

- More detailed information is available in sub-folders.

- Please consider to cite our paper if you use the code or data in your research project.

  > ```
  > bib placeholder.
  > ```
