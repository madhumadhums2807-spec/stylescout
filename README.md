## The catalogue
`data/catalog_source.csv` + `data/images/` come from the Kaggle dataset
[Fashion Product Images (Small)](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small)
by Param Aggarwal. Licence: MIT (as listed on the Kaggle page).

`python -m scripts.import_catalog --source <folder with images/>` cleans the categories/colours,
holds out 87 photos for testing, and writes `data/products.json`.
Prices (`price_inr`) and store names are sample values supplied with the catalogue, not live data.
After changing the catalogue, delete `data/stylescout.db` and `data/faiss.*` and restart.