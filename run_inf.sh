#!/bin/bash
while IFS= read -r line; do
	text=$(echo $line | cut -d "|" -f2)
	path=$(echo $line | cut -d "|" -f1 | cut -d"/" -f8)
	filename=$(echo $line | cut -d "|" -f1 | cut -d"/" -f9)
	# ARG_A= $2
	VAL=12
	TOKEN_COUNT=$( echo $text | wc -w )
	CHAR_COUNT=${#text}
	DIFF=$(($CHAR_COUNT-$TOKEN_COUNT-1))
	ARG_N=$(($DIFF * $VAL))
	
	echo $text;
	echo $path;
	# echo $new_folder;
	python inference.py \-c config_dir/harvard_libritts/config_louisa.json \
	\-f "1841_attn_0_ignore_trim/model_140000" \-w "models/waveglow_256channels_universal_v4.pt" \
	\-t "$text" \-i 1841 \-s 0.75 \-g 1 \-o "/local/anasbori/synth4/$path" \-n ${ARG_N};
	mv /local/anasbori/synth4/$path/sid1841_sigma0.75.wav /local/anasbori/synth4/$path/$filename; 
	# mv "$new_folder" "/local/anasbori/synth/$new_folder";
	# scp -r results anasbori@login2:/local/anasbori/1841_4000_6k_${ARG_A};
done < $1 
