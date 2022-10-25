from .config import ClusterConfiguration
from ..utils.pretty_print import RayCluster
from ..utils import pretty_print
import openshift as oc
from typing import List, Optional


class Cluster:
    def __init__(self, config: ClusterConfiguration):
        self.config = config

    # creates a new cluser with the provided or default spec
    def up(self):
        pass

    def down(self, name):
        pass

    def status(self, print_to_console=True):
        cluster = _ray_cluster_status(self.config.name)
        if cluster:
            if print_to_console:
                pretty_print.print_clusters([cluster])                
            return cluster.status
        else:
            return None
        

def list_all_clusters(print_to_console=True):
    clusters = _get_ray_clusters()
    if print_to_console:
        pretty_print.print_clusters(clusters)
    return clusters


# private methods

def _get_appwrappers(namespace='default'):
    with oc.project(namespace), oc.timeout(10*60):
        app_wrappers = oc.selector('appwrappers').qnames()
    return app_wrappers


def _ray_cluster_status(name, namespace='default') -> Optional[RayCluster]:

    with oc.project(namespace), oc.timeout(10*60):
        cluster = oc.selector(f'rayclusters/{name}').object()

    if cluster:
        return _map_to_ray_cluster(cluster)
    else:
        return None
    



def _get_ray_clusters(namespace='default') -> List[RayCluster]:
    list_of_clusters = []

    with oc.project(namespace), oc.timeout(10*60):
        ray_clusters = oc.selector('rayclusters').objects()

    for cluster in ray_clusters:
        list_of_clusters.append(_map_to_ray_cluster(cluster))
    return list_of_clusters


def _map_to_ray_cluster(cluster):
    cluster_model = cluster.model
    return RayCluster(
        name=cluster.name(), status=cluster_model.status.state,
        min_workers=cluster_model.spec.workerGroupSpecs[0].replicas,
        max_workers=cluster_model.spec.workerGroupSpecs[0].replicas,
        worker_mem_max=cluster_model.spec.workerGroupSpecs[
            0].template.spec.containers[0].resources.limits.memory,
        worker_mem_min=cluster_model.spec.workerGroupSpecs[
            0].template.spec.containers[0].resources.requests.memory,
        worker_cpu=cluster_model.spec.workerGroupSpecs[0].template.spec.containers[0].resources.limits.cpu,
        worker_gpu=0)