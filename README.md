# Apache-Beam/Dataflow Left Join example
This GitHub repo contains the implemented Left Join PTransform.

The PTransform code uses 2 classes, namely the LeftJoin Ptransform class and the UnnestCoGrouped DoFn class. The LeftJoin is a Composite PTransform that uses dictionary comprehension and Map to format the source and join data as suitable cogroupby tuples. It then uses the built-in CoGroupByKey PTransform to group them together by common_key. The last part is to unnest the grouped dictionaries and emit the updated dictionaries which is done using the UnnestCogrouped DoFn.

See my blog here https://nl.devoteam.com/en/blog-post/implementing-left-join-google-dataflow-apache-beam/ for an in depth explanation of the implementation with examples.