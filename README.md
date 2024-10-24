# Keras Tuner Alpha

This repository contains Keras Tuners prototypes.

# Set up

### 1. Clone this repo with submodules

```
git clone --recursive https://github.com/wenxindongwork/keras-tuner-alpha.git
```

#### Or if already cloned:

```
git submodule update --init --recursive
```

#### Troubleshooting

If you don't see the maxtext repository, try

```
git submodule add --force https://github.com/google/maxtext
```

### 2. Install dependencies

```
pip install -r requirements.txt
pip install libtpu-nightly==0.1.dev20240925+nightly -f https://storage.googleapis.com/jax-releases/libtpu_releases.html

```

# Examples

## Tune a HF model

Example of LoRA finetuning gemma2-2b.

```
python keras_tuner/examples/hf_gemma_example.py
```

## Tune a MaxText model

Example of training a MaxText model.

```
python keras_tuner/examples/maxtext_default_example.py
```

## Running examples via Ray

Ray is a great tool for running distributed TPU workloads. Here is an example of how to use Ray to run the examples we mentioned above.

1. Assume you have resource capacity and quota in your GCP project and region/zone. Modify `examples/ray/cluster.yaml` template with your configurations.

2. Run the following command to bring up your ray cluster.

```
ray up -y examples/ray/cluster.yaml
```

Monitor the node set up process by running

```
ray monitor examples/ray/cluster.yaml
```

While you monitor the node set up process, launch the ray dashboard.

```
ray dashboard examples/ray/cluster.yaml
```

You should see the dashboard on your `localhost:8265`

**Troubleshooting**:

- You can also exec into the ray head node using `ray attach examples/ray/cluster.yaml` and run `ray status` to see the status of the nodes.

- If you see an `update-failed` error, don't worry. This should not affect the nodes being properly set up.

3. Once all nodes in your ray cluster are set up and active, and you have launched the dashboard, submit the HuggingFace gemma example using the following commands.

You only need to set this environment variable once.

```
export RAY_ADDRESS="http://127.0.0.1:8265"
```

```
python examples/ray/submit_ray_job.py "python examples/ray/hf_gemma_example_via_ray.py" --hf-token your_token
```

You can terminate your job using 

```ray job stop ray_job_id```

4. Once you are done with your ray cluster, tear it down

`ray down examples/ray/cluster.yaml`
