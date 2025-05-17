def validate_and_extract_params(params, required_keys, optional_keys=None):
	missing_keys = [key for key in required_keys if params.get(key) is None]
	if missing_keys:
		raise ValueError(
			f"Missing required parameters: {', '.join(missing_keys)}")

	extracted_params = {key: params[key] for key in required_keys}
	if optional_keys:
		for key in optional_keys:
			if params.get(key):
				extracted_params[key] = params[key]

	return extracted_params