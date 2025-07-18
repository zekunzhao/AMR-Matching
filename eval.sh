#!/bin/bash
#SBATCH --time=1:00:00 --output=eval.out --error=eval.err
#SBATCH --mem=5GB
#SBATCH -c 5

# python3 src/prompt_eval.py $1 $2 $3

# python3 src/eval.py $1 $2 $3

# ./eval.sh Q1_gold.txt answers/reworded_qs_Lab_105_questions_and_typed_responses_paraphrased.txt

#!/bin/bash


# dirA="../SIcurric/annotator"
# dirB="../SIcurric/gold"
# outdir="SIcurric_output"

dirA="./answers"
outdir="./answers/output"

mkdir -p "$outdir"
for fileA in "$dirA"/*; do
    filename=$(basename "$fileA")
    name="${filename%.*}"
    # fileB="$dirB/$filename"
    if [[ -f "$fileA" ]]; then
        echo "Processing $fileA..."
        outfile="$outdir/${name}.out"
        python3 src/eval.py Q1_gold.txt "$fileA" > "$outfile"
    fi
done