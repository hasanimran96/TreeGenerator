# Media Computing Project

## Plugin for Fusion 360

## Envirogen (Tree Generator)

<img src=https://github.com/hasanimran96/TreeGenerator/blob/master/heroshot.png/>

EnviroGen is a one-stop solution to add trees to the environment of your project. Beit a number of simple trees or a detailed tree, EnviroGen has you covered. Run ourAdd-In on your Fusion project, select the place where you want to have a tree, thesize and done! Your very own tree, uniquely generated every time, is ready to makeyour project all the more beautiful. There are also customisation options available tofit the trees to your demands.

### Project Pitch

#### The opportunity

Suppose you are an architect, you just finished your very important and prestigious project. Your presentation is coming up and you need to present it to the customer. To make the graphics more appealing you want to show it in a realistic scenario but you’re short on time.

Designing a whole environment from scratch is very time consuming and using the same models for the same things e.g tress/cars over and over again looks unnatural and sterile. Wouldn’t it be great to have a way to easily solve this problem?

#### The idea

We propose the idea to design a Fusion 360 plugin for the above problem. The plugin would generate various different Models, for example trees, cars, or people. It will have parameters to adjust the Models for example we can adjust the size range, or the design details to make it different each time.

Now imagine, the architect could use our plugin to create models for a lively environment for his project. He would then be able to create a much more appealing presentation without spending a lot of his time on creating the environmental models and can focus on more important tasks instead.

#### To Run the Plugin

- You will find the Plug-In under the “SOLID” menu in the category “CREATE”
- Start the EnviroGen Plug-In from the category “CREATE” in the “SOLID”menu.
- Select the location where the tree will be generated. It can be:
  - A construction point / vertex
  - Or a surface (the tree will be placed on its centroid)
  - Or none (the tree will be generated at the origin [0,0,0] of the Design)
- Choose a height for the tree.
  - Due to the random generation of the trees, the final height mightdeviate.
- Tick the box “Customize tree”. More options will show up in the menu.
- To change a parameter, click on the arrow next to its name to expand the view.
- Adjust the sliders according to your preferences. Tooltips and Graphics willexplain the effect on the generated trees.
- Click “OK” to generate a tree or cancel to abort. A progress dialog will showup. Due to the random generation, this is an estimation and the process mightfinish before reaching 100%. This is intended and does not mean the tree wasnot finished.
