# contextualized-topic-models-ssl

UPDATE: Parent Paper Implementation has now been moved to [Colab Notebook](https://colab.research.google.com/drive/14t_9WrK5MJ_I0Bx2UCnKV7f1VWHFQMHU?usp=sharing).

Contextualized Topic Models on Same Script Languages

Steps to replicate original model.
1. Install VSCode
2. Update relative paths in the setup scripts as in the example below:

Original
```
with open('README.rst') as readme_file:
```

Updated
```
with open('contextualized-topic-models\README.rst') as readme_file:
```
*Note: You can right click on the file and select "Copy Relative Path".*

3. Run the setup.py file by typing the following in the VSCode Terminal:
```
python contextualized-topic-models\setup.py install
```
This will start installing required packages in their specified versions. You may need to install updated C++ tools from Visual Studio from [here](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16).
