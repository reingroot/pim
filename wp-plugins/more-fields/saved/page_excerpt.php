<?php 
add_filter('more_fields_saved', 'more_fields_saved_page_excerpt');
function more_fields_saved_page_excerpt ($d) {$d['page-excerpt'] = maybe_unserialize('a:6:{s:5:"label";s:12:"Page excerpt";s:8:"position";s:4:"left";s:5:"index";s:12:"page-excerpt";s:12:"ancestor_key";s:0:"";s:6:"fields";a:1:{s:7:"excerpt";a:8:{s:5:"label";s:7:"Excerpt";s:3:"key";s:12:"page-excerpt";s:4:"slug";s:0:"";s:10:"field_type";s:8:"textarea";s:6:"values";s:0:"";s:7:"caption";s:71:"Write your caption for this page here. Will be used on the parent page.";s:5:"index";s:7:"excerpt";s:12:"ancestor_key";s:0:"";}}s:10:"post_types";a:1:{i:0;s:4:"page";}}', true); return $d; }
?>