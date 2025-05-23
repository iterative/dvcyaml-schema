# dvcyaml-schema

[JSON Schema](https://json-schema.org/) for [`dvc.yaml`](https://dvc.org/doc/user-guide/dvc-files-and-directories#dvcyaml-file) file format, generated using [Pydantic](https://docs.pydantic.dev/latest/).

It can provide better autocompletion, validation, and linting for `dvc.yaml` files.

## Usage

#### Visual Studio Code (with [YAML Extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)):

If you have installed the  [YAML Extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml), it will automatically fetch the latest `dvc.yaml` schema, and work out of the box.

Alternatively, you can explicitly configure it by adding the following to your settings:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/iterative/dvcyaml-schema/master/schema.json":
        "dvc.yaml"
  }
}
```

You can also specify custom URL or path instead for debugging/testing purposes.

#### JetBrain IDEs (PyCharm, Intellij IDEA, et al.)

JetBrain IDEs automatically fetch the latest `dvc.yaml` schema and should work without additional setup.

If you're using an older version or encounter any issues, refer to this [guide](https://www.jetbrains.com/help/ruby/yaml.html#remote_json) for assistance.

#### Other Editors

`dvc.yaml` schema is available in [JSON Schema Store](https://www.schemastore.org/json/), so it will be pulled automatically in editors that support it
natively or through plugins.

To add it manually, use the following URL to obtain the latest JSON schema for `dvc.yaml`:

```
https://raw.githubusercontent.com/iterative/dvcyaml-schema/master/schema.json
```

Check the documentation of your specific editor or IDE for details on how to configure schemas.

### Important Files:

1. **[schema.json](schema.json)**
2. [gen.py](gen.py)
3. [examples](examples)
4. [tests.py](tests.py)

### Contributing

1. Setup your environment (you'll need `python3.10+` and `pip`).
    ```console
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ pre-commit install
    ```
2. Generate the schema.

   The schema is generated using [Pydantic](https://docs.pydantic.dev/latest/) through the [gen.py](gen.py) script. You can make adjustments to the script as needed.

   To manually generate the schema, run:
    ```console
    $ ./gen.py schema.json
    ```

3. (Optional) Add [valid](examples/valid) and [invalid](examples/invalid) yaml examples.
4. Run tests using:
    ```console
    $ pytest
    ```
5. Git-add the changes and then commit. `pre-commit` hook should run automatically and format/lint code, regenerate new schema, and run tests.
    ```console
    $ git add -p
    $ git commit -m "<message>"
    ```

    If the hook makes additional changes, stage them and attempt the commit again.

6. Send us a pull request. 🤗
