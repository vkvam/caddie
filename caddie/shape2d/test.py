def combine_lists(base_list, other_lists):
    combined = []
    base_len = len(base_list)

    for other_list in other_lists:
        # Validate if the list length is a multiple or an inverse multiple of the base list's length
        if len(other_list) % base_len != 0 and base_len % len(other_list) != 0:
            raise ValueError(f"List length {len(other_list)} is not a valid multiple or inverse multiple of the base list length {base_len}.")


    for i, base_item in enumerate(base_list):
        combined_group = [[base_item]]  # Start with a sublist containing the base item

        for lst in other_lists:
            lst_len = len(lst)

            if lst_len >= base_len:
                # Group items from the larger list with the base item
                chunk_size = lst_len // base_len
                combined_group.append(lst[i * chunk_size: (i + 1) * chunk_size])
            else:
                # Repeat the item from the smaller list for each element in the base list
                combined_group.append([lst[i % lst_len]])

        combined.append(combined_group)

    return combined
