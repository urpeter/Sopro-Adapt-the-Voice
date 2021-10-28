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
	python inference.py \-c config_louisa.json \
	\-f "1841_attn_0_ignore_trim/model_140000" \-w "models/waveglow_256channels_universal_v4.pt" \
	\-t "$text" \-i 1841 \-s 0.75 \-g 1 \-o "somepath/$path" \-n ${ARG_N};
	mv somepath/$path/sid1841_sigma0.75.wav somepath/$path/$filename; 
	#mv "$new_folder" "somepath/$new_folder";
	#scp -r results somepath/1841_4000_6k_${ARG_A};
done < $1 
