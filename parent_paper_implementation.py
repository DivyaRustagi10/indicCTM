# -*- coding: utf-8 -*-
"""Parent Paper Implementation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NLvwnjfTRZs-pp4C0tRxbODiwoOj1ysv

#To contextualize or to not contextualize?

> Can we define a topic model that does not rely on the BoW input but instead uses contextual information?

First, we want to check if ZeroShotTM maintains comparable performance to other topic models; if this is true, we can then explore its performance in
a cross-lingual setting. Since we use only English text, in this setting we use English representations.
"""

# Commented out IPython magic to ensure Python compatibility.
# # Install the contextualized topic model library
# %%capture
# !pip install contextualized-topic-models==2.2.0

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install pyldavis
# !pip install wget
# !pip install head

"""We replace the input BoW in Neural-ProdLDA
with pre-trained multilingual representations from
SBERT (Reimers and Gurevych, 2019), a recent and effective model for contextualized representations.

Indeed, ZeroShotTM
is language-independent: given a contextualized
representation of a new language as input,1
it can
predict the topic distribution of the document. The
predicted topic descriptors, though, will be from
the training language. Let us also notice that our
method is agnostic about the choice of the neural
topic model architecture (here, Neural-ProdLDA),
as long as it extends a Variational Autoencoder.

# Data

### Building Comparable Documents
Datasets We use datasets collected from English
Wikipedia abstracts from DBpedia. The first dataset (W1) contains 20,000 randomly sampled abstracts. The second dataset (W2) contains 100,000 English documents. 

We use 99,700 documents as
training and consider the remaining 300 documents as the test set. We collect the 300 respective instances in Portuguese, Italian, French, and German.

### Building W1
"""

import wget
wget.download("https://raw.githubusercontent.com/vinid/data/master/dbpedia_sample_abstract_20k_unprep.txt")

text_file = "dbpedia_sample_abstract_20k_unprep.txt" # EDIT THIS WITH THE FILE YOU UPLOAD

"""### Importing"""

from contextualized_topic_models.models.ctm import ZeroShotTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from contextualized_topic_models.utils.preprocessing import WhiteSpacePreprocessing
import nltk
import pickle

"""### Preprocessing
Why do we use the preprocessed text here? We need text without punctuation to build the bag of word. Also, we might want only to have the most frequent words inside the BoW. Too many words might not help.
"""

nltk.download('stopwords')

documents = [line.strip() for line in open(text_file, encoding="utf-8").readlines()]
sp = WhiteSpacePreprocessing(documents, stopwords_language='english')
preprocessed_documents, unpreprocessed_corpus, vocab = sp.preprocess()

preprocessed_documents[:2]

"""We don't discard the non-preprocessed texts, because we are going to use them as input for obtaining the contextualized document representations.

Let's pass our files with preprocess and unpreprocessed data to our TopicModelDataPreparation object. This object takes care of creating the bag of words for you and of obtaining the contextualized BERT representations of documents. This operation allows us to create our training dataset.

Note: Here we use the contextualized model "distiluse-base-multilingual-cased", because we need a multilingual model for performing cross-lingual predictions later.
"""

# Building W1
tp = TopicModelDataPreparation("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

training_dataset = tp.fit(text_for_contextual=unpreprocessed_corpus, text_for_bow=preprocessed_documents)

pickle.dump(training_dataset, open('training_dataset.txt', 'wb'), pickle.HIGHEST_PROTOCOL)

tp.vocab[:10]

"""## M1. Training Zero-Shot Contextualized Topic Model

Finally, we can fit our new topic model. We will ask the model to find 50 topics in our collection (n_component parameter of the CTM object).
"""

#with open('training_dataset.obj', "rb") as fr:
#  training_dataset = pickle.load(fr)
type(training_dataset)

# 100 topics over 100 runs
ctm = ZeroShotTM(bow_size=len(tp.vocab), contextual_size=768, n_components=100, num_epochs=100)
ctm.fit(training_dataset) # run the model

"""**1.1. Get Topics**

After training, now it is the time to look at our topics: we can use the


```
get_topic_lists
```
function to get the topics. It also accepts a parameter that allows you to select how many words you want to see for each topic.

If you look at the topics, you will see that they all make sense and are representative of a collection of documents that comes from Wikipedia (general knowledge). Notice that the topics are in English, because we trained the model on English documents.
"""

ctm.get_topic_lists(5)

"""**1.2. Get Topic Prediction**"""

topics_predictions = ctm.get_thetas(training_dataset, n_samples=30) # get all the topic predictions
#topics_predictions = ctm.get_thetas(training_dataset, n_samples=100) # get all the topic predictions

preprocessed_documents[0] # see the text of our preprocessed document

import numpy as np
topic_number = np.argmax(topics_predictions[0]) # get the topic id of the first document

ctm.get_topic_lists(5)[topic_number] #and the topic should be about natural location related things

import pickle
pickle.dump(preprocessed_documents, open('preprocessed_documents.txt', 'wb'), pickle.HIGHEST_PROTOCOL)

# Get NPMI Coherence
from contextualized_topic_models.evaluation.measures import CoherenceNPMI

with open('preprocessed_documents.txt', "rb") as fr:
  fr = pickle.load(fr)
  texts = [doc.split() for doc in fr] # load text for NPMI
  npmi = CoherenceNPMI(texts=texts, topics=ctm.get_topic_lists(50))
  npmi_100 = CoherenceNPMI(texts=texts, topics=ctm.get_topic_lists(100))
  print(npmi.score())
  print(npmi_100.score())

"""## M2. Training Neural-ProdLDA

We use the implementation made available by [Carrow (2018)](https://github.com/estebandito22/PyTorchAVITM/blob/master/README.md).

**Model Training Instructions**

* Epochs = 100
* ADAM optimizer -> learning rate = 2e-3. 
* The inference network is composed of a single hidden layer and 100-dimension of softplus units. 
* The priors over the topic and
document distributions are **learnable parameters**.
* Momentum = 0.99, learning rate = 0.002, and we apply 20% of drop-out to the hidden document representation. 
* Batch size = 200
"""

print("hello")

"""### M3. Training LDA

We use [Gensim’s](https://radimrehurek.com/gensim/models/ldamodel.html) implementation of this model.

**Model Training Instructions**

The hyper-parameters alpha and beta, controlling the document-topic and word-topic distribution respectively, are estimated from the data during training.
"""



"""## M4. Training Combined TM
CTMs work better when the size of the bag of words has been restricted to a number of terms that does not go over 2000 elements. This is because we have a neural model that reconstructs the input bag of word, Moreover, in CombinedTM we project the contextualized embedding to the vocab space, the bigger the vocab the more parameters you get, with the training being more difficult and prone to bad fitting. 

**Model Training Instructions**

* Epochs = 100
* ADAM optimizer
* Hyperparameters are the same used for Neural-ProdLDA with the difference that we also use SBERT features in combination with the BoW.
* We take the SBERT embeddings, apply a (learnable) function/dense layer R^512 → R^|V|and concatenate the representation to the BoW. 
"""

from contextualized_topic_models.models.ctm import CombinedTM

ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, n_components=20, num_epochs=10)
ctm.fit(training_dataset) # run the model

ctm.get_topic_lists(5)

"""### Topic Predictions"""

topics_predictions = ctm.get_thetas(training_dataset, n_samples=5) # get all the topic predictions

import numpy as np
topic_number = np.argmax(topics_predictions[0]) # get the topic id of the first document

ctm.get_topic_lists(5)[18]
ctm.get_topic_lists(5)[topic_number] #and the topic should be about natural location related things

"""### Saving Models"""

ctm.save(models_dir="./")
# let's remove the trained model
del ctm

ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, num_epochs=100, n_components=50)

ctm.load("/content/contextualized_topic_model_nc_50_tpm_0.0_tpv_0.98_hs_prodLDA_ac_(100, 100)_do_softplus_lr_0.2_mo_0.002_rp_0.99",
                                                                                                      epoch=19)
ctm.get_topic_lists(5)

"""# Zero-shot Cross-Lingual Topic Modeling
> Can the conxtextualized TM tackle zero-shot cross-lingual topic modeling?

ZeroShotTM can be used for zero-shot cross-lingual topic modeling. 

First, we use SBERT to generate multilingual embeddings as the input of the model. Then we evaluate multilingual topic predictions on the multilingual abstracts in W2.
"""



"""### Quantitative Evaluation
Metrics
1. **Matches**:
% of times the predicted topic for the non-English test document is the same as for the respective test document in English. The higher the scores, the better.

2. **Centroid Embeddings**: To also account for similar but not exactly equal
topic predictions, we compute the centroid embeddings of the 5 words describing the predicted topic for both English and non-English documents. Then we compute the cosine similarity between those two centroids (CD).

3. **Distributional Similarity**: Compute the KL divergence between the predicted topic distribution on the test document
and the same test document in English. Lower scores are better, indicating that the distributions do not differ by much.

> /Desktop/ctm_implementation/contextualized-topic-models/contextualized_topic_models/evaluation/measures.py


"""