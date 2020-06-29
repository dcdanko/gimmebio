
clean:
	rm .gimmebio_data_manager.sqlite


add:
	touch .gimmebio_data_manager.sqlite
	gimmebio data add key foo bar bizz
	gimmebio data add files -l file_list.txt
	gimmebio data run md5
	gimmebio data list keys
	gimmebio data list files
