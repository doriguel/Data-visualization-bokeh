units_code="""
        var selected = units_selection.active;
        if(selected==0){
            x_selection.options=xy_options_metric;
            x_selection.value="kpl";
            y_selection.options=xy_options_metric;
            y_selection.value="hp";
            resize_selection.options=resizeby_options_metric;
            resize_selection.value="None";
        } else{
            x_selection.options=xy_options_imper;
            x_selection.value="mpg";
            y_selection.options=xy_options_imper;
            y_selection.value="hp";
            resize_selection.options=resizeby_options_imper;
            resize_selection.value="None";
        }
        source.change.emit();
        """
js_code_x="""
        var new_data = source.data[x_selection.value];
        source.data['x_active'] = new_data;
        // Update axis labels to reflect what was selected
        xaxis1[0].axis_label = x_selection.value;
        xaxis2[0].axis_label = x_selection.value;
        title1.text = `${y_selection.value} vs ${x_selection.value}`;
        title2.text = `${y_selection.value} vs ${x_selection.value}`;

        function onlyUnique(value, index, self){
        return self.indexOf(value) === index;
        }

        var filtered_new_data = new_data.filter(onlyUnique);

        fig0.x_range = filtered_new_data.sort();
        fig1.x_range = filtered_new_data.sort();

        // Mutate source.data in-place
        source.change.emit();
        fig0.change.emit();
        fig1.change.emit();
        """
js_code_y = """
        var new_data = source.data[y_selection.value];
        source.data['y_active'] = new_data;
        // Update axis labels to reflect what was selected
        yaxis1[0].axis_label = y_selection.value;
        yaxis2[0].axis_label = y_selection.value;
        title1.text = `${y_selection.value} vs ${x_selection.value}`;
        title2.text = `${y_selection.value} vs ${x_selection.value}`;

        function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
        }

        var filtered_new_data = new_data.filter(onlyUnique);

        fig0.y_range.factors = filtered_new_data.sort();
        fig1.y_range.factors = filtered_new_data.sort();

        // Mutate source.data in-place
        source.change.emit();
        fig0.change.emit();
        fig1.change.emit();
    """
js_code_cat = """
        var selection = categ_selection.value;
        var field1 = legend1.items;
        var field2 = legend2.items;

        function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
        }

        if(selection=="None"){
            var categories = source.data["Nonecol"];
            //Get unique values of the category selection
            var cat_unique = categories.filter(onlyUnique);
            //Assign subcategories to the subcategory selection
            subcateg_selection.options = cat_unique;
        } else{
            var categories = source.data[selection];
            //Get unique values of the category selection
            var cat_unique = categories.filter(onlyUnique);
            cat_unique.sort();
            //Assign subcategories to the subcategory selection
            subcateg_selection.options = cat_unique;
        }

        //Assign empty values before starting to populate the legend
        for(var i=0; i<field1.length; i++){
            field1[i].label = "";
            field2[i].label = "";
        }
        //Populate legend with new items
        for(var i=0; i<cat_unique.length; i++){
            group_filter[i].group = cat_unique[i];
            filtered_views[i].filters = [group_filter[i]];
            field1[i].label = cat_unique[i];
            field2[i].label = cat_unique[i];
        }
        source.data['category'] = categories;

        //Rename the legend
        legend1.title = categ_selection.value;
        legend2.title = categ_selection.value;

        // Mutate source.data in-place
        source.change.emit();
        subcateg_selection.change.emit();
    """
js_code_subcat = """
        var selected_vals = subcateg_selection.value;
        var field1 = legend1.items;
        var field2 = legend2.items;
        var index1_check = [];
        var index2_check = [];

        if(selected_vals.length >= 1){
            for(var i=0; i<field1.length; i++){
                index1_check[i]=selected_vals.indexOf(field1[i].label.value);
                index2_check[i]=selected_vals.indexOf(field2[i].label.value);
                    if((index1_check[i])>=0){
                        field1[i].renderers[0].visible = true;
                        //field1[i].label.visible = true;
                        field2[i].renderers[0].visible = true;
                        //field2[i].label.visible = true;
                    }
                    else{
                        field1[i].renderers[0].visible = false;
                        //field1[i].label.visible = false;
                        field2[i].renderers[0].visible = false;
                        //field2[i].label.visible = false;
                    }
            }
        } else{
            for(var i=0; i<field1.length; i++){
                field1[i].renderers[0].visible = true;
                //field1[i].label.visible = true;
                field2[i].renderers[0].visible = true;
                //field2[i].label.visible = true;
                }
            }
        // Mutate source.data in-place
        source.change.emit();
        """
js_code_res = """
        source.data['sizes'] = source.data[resize_selection.value];
        var source_sizes = source.data['sizes'];
        var maxval = Math.max(...source_sizes);
        var minval = Math.min(...source_sizes);

        for(var i=0;i<sizes0.length;i++){
            sizes0[i]['field'] = source_sizes;
            sizes1[i]['field'] = source_sizes;
            sizes0[i]['transform'].x = [minval, maxval];
            sizes1[i]['transform'].x = [minval, maxval];
        }
        // Mutate source.data in-place
        source.change.emit();
        """
display_code = """
        const attrs = %s;
        const args = [];
        var selected_index = source.selected.indices[0];
        var info = [source.data.name[selected_index],
                    source.data.mfr[selected_index],
                    source.data.origin[selected_index],
                    source.data.yr[selected_index],
                    source.data.accel[selected_index],
                    source.data.hp[selected_index],
                    source.data.displ[selected_index]];
        if (source.selected.indices.length > 0){
            for (let i = 0; i<attrs.length; i++) {
                args.push(attrs[i].bold() + ' = '.bold() + info[i]);
            }
            const line = "<span style=%r>" + args.join("<br />") + "</span>\\n";

            const text = div.text.concat(line);
            const lines = text.split("\\n")
            if (lines.length > 2)
                lines.shift();
            div.text = lines.join("\\n");
        }
    """