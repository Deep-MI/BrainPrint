"""
Default application configuration.
"""

from typing import Dict

BRAINPRINT_RESULTS_DIR: str = "brainprint"
EIGENVECTORS_DIR: str = "eigenvectors"
EIGENVECTORS_SUFFIX_TEMPLATE: str = ".evecs-{key}.csv"
SURFACES_DIR: str = "surfaces"
TEMP_DIR: str = "temp"
TEMP_ASEG_TEMPLATE: str = "temp/aseg.{uid}"
RELATIVE_ASEG_MGZ_PATH: str = "mri/aseg.mgz"
RELATIVE_NORM_MGZ_PATH: str = "mri/norm.mgz"
RELATIVE_SURFACE_TEMPLATE: str = "surfaces/aseg.final.{indices}.vtk"
SURFACE_NAME_TEMPLATE: str = "{name}.surf"
CSV_NAME_TEMPLATE: str = "{subject_id}.brainprint.csv"
COMMAND_TEMPLATES: Dict[str, str] = {
    "test": "mri_binarize -version",
    "mri_binarize": "mri_binarize --i {source} --match {match} --o {destination}",
    "mri_pretess": "mri_pretess {source} {label_value} {norm_path} {destination}",
    "mris_convert": "mris_convert {source} {destination}",
    "mri_mc": "mri_mc {source} {label_value} {destination}",
}
SHAPEDNA_KWARGS = {
    "lump": False,
    "aniso": None,
    "aniso_smooth": 10,
}
ASEG_LABELS = {
    "CorpusCallosum": ["251", "252", "253", "254", "255"],
    "Cerebellum": ["7", "8", "16", "46", "47"],
    "Ventricles": ["4", "5", "14", "24", "31", "43", "44", "63"],
    "3rd-Ventricle": ["14", "24"],
    "4th-Ventricle": ["15"],
    "Brain-Stem": ["16"],
    "Left-Striatum": ["11", "12", "26"],
    "Left-Lateral-Ventricle": ["4", "5", "31"],
    "Left-Cerebellum-White-Matter": ["7"],
    "Left-Cerebellum-Cortex": ["8"],
    "Left-Thalamus-Proper": ["10"],
    "Left-Caudate": ["11"],
    "Left-Putamen": ["12"],
    "Left-Pallidum": ["13"],
    "Left-Hippocampus": ["17"],
    "Left-Amygdala": ["18"],
    "Left-Accumbens-area": ["26"],
    "Left-VentralDC": ["28"],
    "Right-Striatum": ["50", "51", "58"],
    "Right-Lateral-Ventricle": ["43", "44", "63"],
    "Right-Cerebellum-White-Matter": ["46"],
    "Right-Cerebellum-Cortex": ["47"],
    "Right-Thalamus-Proper": ["49"],
    "Right-Caudate": ["50"],
    "Right-Putamen": ["51"],
    "Right-Pallidum": ["52"],
    "Right-Hippocampus": ["53"],
    "Right-Amygdala": ["54"],
    "Right-Accumbens-area": ["58"],
    "Right-VentralDC": ["60"],
}
CORTICAL_LABELS = {
    "lh-white-2d": "lh.white",
    "rh-white-2d": "rh.white",
    "lh-pial-2d": "lh.pial",
    "rh-pial-2d": "rh.pial",
}
LATERAL_STRUCTURES = [
    ("Left-Striatum", "Right-Striatum"),
    ("Left-Lateral-Ventricle", "Right-Lateral-Ventricle"),
    (
        "Left-Cerebellum-White-Matter",
        "Right-Cerebellum-White-Matter",
    ),
    ("Left-Cerebellum-Cortex", "Right-Cerebellum-Cortex"),
    ("Left-Thalamus-Proper", "Right-Thalamus-Proper"),
    ("Left-Caudate", "Right-Caudate"),
    ("Left-Putamen", "Right-Putamen"),
    ("Left-Pallidum", "Right-Pallidum"),
    ("Left-Hippocampus", "Right-Hippocampus"),
    ("Left-Amygdala", "Right-Amygdala"),
    ("Left-Accumbens-area", "Right-Accumbens-area"),
    ("Left-VentralDC", "Right-VentralDC"),
]
LATERAL_STRUCTURES_2D = [
    ("lh-white-2d", "rh-white-2d"),
    ("lh-pial-2d", "rh-pial-2d"),
]


# flake8: noqa: E501
