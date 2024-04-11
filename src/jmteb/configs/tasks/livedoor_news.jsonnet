{
  livedoor_news: {
    class_path: 'ClusteringEvaluator',
    init_args: {
      test_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'test',
          name: 'livedoor_news',
        },
      },
      dev_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'validation',
          name: 'livedoor_news',
        },
      },
    },
  },
}
