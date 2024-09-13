from eval_ucf101 import UCFclassification
from eval_kinetics import KINETICSclassification
from eval_adni import ADNIclassification



# ucf_classification = UCFclassification('../annotation_UCF101/ucf101_01.json',
#                                        '../results/val.json',
#                                        subset='validation', top_k=1)
# ucf_classification.evaluate()
# print(ucf_classification.hit_at_k)


adni_classification = ADNIclassification('../adni/test.csv',
                                       '../results/val.json',
                                       subset='validation',
                                       top_k=1,
                                       check_status=False)
adni_classification.evaluate()
