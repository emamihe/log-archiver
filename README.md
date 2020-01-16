# log-archiver

python script to ship archive logs to aliyun oss

```
python archiver.py --config config.json
```

# config file

Here is the sample config for config.json

```
{
	"DataDir": "/var/lib/log-archiver/",
	"LogFile": "/var/log/log-archiver/events.log",
	"LogLevel": "INFO",
	"AppendDataTimeToNameOfFile": "true",
	"Collectors": {
		"LogPath": [
			"/var/log/nginx/*.2.gz",
			"/var/tmp/somelogs/*"
		]
	},
	"Aliyun": {
		"AccessKeyID": "<ENTER-YOUR-ACCESS-KEY-ID-HERE>",
		"AccessKeySecret": "<ENTER-YOUR-ACCESS-KEY-SECRET-HERE>",
		"Endpoint": "<ENTER-YOUR-ENDPOINT-HERE>",
		"Prefix": "<ENTER-YOUR-PREFIX-HERE>",
		"BucketName": "<ENTER-YOUR-BUCKET-NAME-HERE>"
	}
}
```
