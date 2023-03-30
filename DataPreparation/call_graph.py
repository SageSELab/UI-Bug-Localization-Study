import javalang
import collections
import networkx as nx
import matplotlib as mpl
mpl.use('TkAgg')  # Configuring matplotlib back-end
import matplotlib.pyplot as plt
try:
    from collections.abc import Iterable as Iterable
except ImportError:
    from collections import Iterable as Iterable

class CallGraph:
	# ---- Simple Visualization for Debuggins ----
    def visualize_call_graph(self, G):
        """Takes a networkx graph and visualizes using matplotlib."""

        pos = nx.spring_layout(G)
        nx.draw(G, pos, font_size=16, with_labels=False) # place labels seperately above node
        for p in pos:  # Raise text positions
            pos[p][1] += 0.1
        nx.draw_networkx_labels(G, pos)
        plt.show()


    # ------------------------------------------------------------------------------
    # ----NetworkX ----

    def create_networkx_graph(self, graph_dict):
        G = nx.DiGraph()  # Directed graph

        for java_class, class_dict in graph_dict.items():
            call_graph = class_dict["called_methods"]
            for callee_method_name, called_methods in call_graph.items():
                #print(callee_method_name)
                G.add_node(callee_method_name)
                for called_method_name in called_methods:
                    G.add_edge(callee_method_name, called_method_name)
        return G


    # https://www.geeksforgeeks.org/python-program-for-depth-first-rch-or-dfs-for-a-graph/
    # A function used by DFS
    def DFSUtil(self, graph, v, visited):
 
        # Mark the current node as visited and print it
        visited.append(v)
 
        # Recur for all the vertices adjacent to
        # this vertex
        for node in graph.neighbors(v):
            if node not in visited:
                self.DFSUtil(graph, node, visited)
 
 
    # The function to do DFS traversal. It uses
    # recursive DFSUtil()
    def DFS(self, graph, list_of_start_methods, class_method_dict, bug_report_contents, rch_terms, visited):
        #print(graph)
        V = len(graph)  #total vertices
 
        # Call the recursive helper function to print
        # DFS traversal starting from all vertices one
        # by one
        methods_on_similarities = []
        all_methods_and_similarities = []
        term_methods = []

        for node in graph:
            if node not in list_of_start_methods:
                continue

            if node not in visited:
                self.DFSUtil(graph, node, visited)

        visited = self.get_unique_names(visited)
        without_terms_method_list = []
        term_class_names = []
        without_terms_class_names = []
        for node in visited:
            class_name, method_block = self.get_method_block_with_file_name(node, class_method_dict)  
            #method_contents_list.append(method_block)

            termFlag = self.check_if_term_exist(rch_terms, method_block)
            #bugReportSimilarFlag, sim_score = self.check_if_similar(bug_report_contents, method_block)

            if termFlag == True:
                term_class_names.append(class_name)
                term_methods.append(method_block)
            else: 
                without_terms_class_names.append(class_name)
                without_terms_method_list.append(method_block)

        #https://www.geeksforgeeks.org/python-concatenate-two-lists-element-wise/
        terms_methods_similarity_scores = self.codeMappingHelper.get_cos_similarity_scores(bug_report_contents, term_methods)

        terms_methods_similarities = []
        for index in range(len(terms_methods_similarity_scores)):
            terms_methods_similarities.append((term_methods[index],terms_methods_similarity_scores[index], term_class_names[index]))
        terms_methods_similarities.sort(key=lambda y:(y[1],y[2]), reverse=True)

        partial_method_content_list = []
        partial_method_name_list = []
        
        for ind in range(len(without_terms_method_list)):
            if ind==0 or ind%100!=0:
                partial_method_content_list.append(without_terms_method_list[ind])
                partial_method_name_list.append(without_terms_class_names[ind])
            else:
                if len(partial_method_content_list)>0:
                    cos_sim_scores = self.codeMappingHelper.get_cos_similarity_scores(bug_report_contents, partial_method_content_list)

                    for i in range(len(cos_sim_scores)):
                        methods_on_similarities.append((partial_method_content_list[i], cos_sim_scores[i], partial_method_name_list[i]))
                    partial_method_content_list = []
                    partial_method_name_list = []

        if len(partial_method_content_list)>0:
            cos_sim_scores = self.codeMappingHelper.get_cos_similarity_scores(bug_report_contents, partial_method_content_list)

            for i in range(len(cos_sim_scores)):
                methods_on_similarities.append((partial_method_content_list[i], cos_sim_scores[i], partial_method_name_list[i]))

        methods_on_similarities.sort(key=lambda y:(y[1],y[2]), reverse=True)

        all_methods = []
        all_classes = []

        for method_block, similarity_score, inside_class in terms_methods_similarities:
            if len(inside_class)>0 and len(method_block)>0:
                all_classes.append(inside_class)
                all_methods.append(method_block)

        for method_block, similarity_score, inside_class in methods_on_similarities:
            #if method_block not in term_methods:
            if len(inside_class)>0 and len(method_block)>0:
                all_methods.append(method_block)
                all_classes.append(inside_class)
        return all_classes, all_methods


    def construct_method_declarations_list(self, declarations):
        """Helper method to convert a list of declarations into dictionary that
        groups by type of declaration."""

        method_declarations = []
        for declaration in declarations:
            if isinstance(declaration, javalang.tree.MethodDeclaration):
                method_declarations.append(declaration)
            elif isinstance(declaration, javalang.tree.ClassDeclaration):
                for inside_declaration in declaration.body:
                    if isinstance(inside_declaration, javalang.tree.MethodDeclaration):
                        method_declarations.append(inside_declaration)
        return method_declarations

    # ------------------------------------------------------------------------------
    # ---- Call Graph Helper Methods ----

    def get_methods_ids_that_match_name(self, name, graph_dict):
        """Takes a method name and a graph_dict and returns a list of method_ids in the graph_dict
        that match the method name."""
        matched_method_ids = []
        for class_name, class_dict in graph_dict.items():
            for method in class_dict["defined_methods"]:
                if name == method.name:
                    matched_method_ids.append(method.id)
        return matched_method_ids


    def create_method_id(self, class_name, name):
        return class_name + '.' + name

    def create_method_id_with_parameters(self, class_name, name, params):
        #print(params)

        method_name_with_params = class_name + '.' + name + '('

        for i in range(len(params)-1):
            method_name_with_params += params[i].type.name + ","

        if len(params)>0:
            method_name_with_params += params[len(params)-1].type.name 

        return method_name_with_params + ')'

    # ------------------------------------------------------------------------------
    # ---- Utilities ----

    def flatten_attributes(self, l):
        """Utility function to because certain Statements are blocks with a list of statements as their attributes"""
        flattened_list = []
        for elem in l:
            if isinstance(elem, Iterable) and not isinstance(elem, (str, bytes)):
                flattened_list.extend(elem)
            elif elem is not None:
                flattened_list.append(elem)
        return flattened_list


    def getopts(self, argv):
        """Collect command-line options in a dictionary. From https://gist.github.com/dideler/2395703"""
        opts = {}  # Empty dictionary to store key-value pairs.
        while argv:  # While there are arguments left to parse...
            if argv[0][0] == '-':  # Found a "-name value" pair.
                opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
            argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
        return opts

    # ------------------------------------------------------------------------------
    # ---- Graph Dictionary Construction ----

    def create_defined_methods_and_fields_dict(self, java_classes):
        """Takes a list of classes and creates a graph_dict that includes the methods defined in each class."""
        graph_dict = {}
        called_method_dict = {}

        for java_class in java_classes:  # Assumes class is not calling methods from other class
            methods_inside_class = [] 
            class_name = java_class.name

            class_dict = {
                            "defined_methods": [],
                            "called_methods" : {}
                         }

            declarations_list = java_class.body  # The declarations in each class as a list

            method_declarations = self.construct_method_declarations_list(declarations_list)  # Intermediate data structure meant for parsing methods of a class

            for method_declaration in method_declarations:
                #method_id = self.create_method_id(class_name, method_declaration.name)
                method_id = self.create_method_id_with_parameters(class_name, method_declaration.name, method_declaration.parameters)
                methods_inside_class.append(method_id)
                method = Method(method_id, method_declaration.name, class_name)
                class_dict["defined_methods"].append(method)

            called_method_dict[class_name] = methods_inside_class
            graph_dict[java_class.name] = class_dict
           
        return graph_dict, called_method_dict


    def construct_class_dict(self, declarations, class_name, graph_dict):
        """Parses method declarations in a class and adds called methods to the graph_dict.
        SIDE EFFECT: modifies graph_dict."""
        class_dict = graph_dict[class_name]

        method_declarations = self.construct_method_declarations_list(declarations)  # Intermediate data structure meant for parsing methods of a class
        for method_declaration in method_declarations:
            #method_id = self.create_method_id(class_name, method_declaration.name)
            method_id = self.create_method_id_with_parameters(class_name, method_declaration.name, method_declaration.parameters)

            # Now figure out which methods this method calls and add to called_methods
            class_dict["called_methods"][method_id] = self.construct_called_methods(class_name, graph_dict, OrderedSet(), method_declaration.body)



    recursive_statements = {javalang.tree.WhileStatement, javalang.tree.BlockStatement, javalang.tree.IfStatement, javalang.tree.BinaryOperation, javalang.tree.Creator, javalang.tree.SwitchStatementCase}


    def add_method(self, class_name, expression, graph_dict):
        # Okay,the goal for now is to just construct a sound call graph (not a precise one), so let's just add an
        # edge to all of the possible options. We can add CHA later to restrict how many edges are added
        #methods = set()
        methods = OrderedSet()

        matched_method_ids = self.get_methods_ids_that_match_name(expression.member, graph_dict)

        if len(matched_method_ids) == 0:  # Method may have been defined in super class. We are constructing a partial graph
            # FIXME: If we add parameters to ID, we'll have a problem here
            methods.add(class_name + '.' + expression.member)

        for matched_method_id in matched_method_ids:
            methods.add(matched_method_id)
        return methods

    def construct_called_methods(self, class_name, graph_dict, called_methods, body):
        if body == None:
            return called_methods
        for method_expression in body:  # The statements/expressions that make up a method
            try:
                expression = method_expression.expression
                if isinstance(expression, javalang.tree.MethodInvocation):  # For each statement that invokes a method
                    called_methods.update(self.add_method(class_name, expression, graph_dict))
                    called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                    called_methods, expression.arguments))  # MethodInvocations may have other nested method Invocations

                if isinstance(expression, (javalang.tree.Assignment, javalang.tree.BinaryOperation)):
                    statement_attributes = [getattr(expression, attr) for attr in expression.attrs]
                    called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                    called_methods, statement_attributes))

                if isinstance(method_expression, javalang.tree.SwitchStatement):
                    called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                    called_methods, method_expression.cases))

            except AttributeError:
                if isinstance(method_expression, javalang.tree.MethodInvocation):  # Sometimes expression is a MethodInvocation itself
                    called_methods.update(self.add_method(class_name, method_expression, graph_dict))
                    called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                    called_methods, method_expression.arguments))  # MethodInvocations may have other nested method Invocations

                if isinstance(method_expression, javalang.tree.TryStatement):
                    called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                    called_methods, method_expression.block))
                    

                if isinstance(method_expression, tuple(self.recursive_statements)):

                    statement_attributes = [getattr(method_expression, attr) for attr in method_expression.attrs]

                    if isinstance(method_expression, (javalang.tree.WhileStatement, javalang.tree.IfStatement, javalang.tree.BinaryOperation)):
                        called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                        called_methods, statement_attributes))

                    elif isinstance(method_expression, (javalang.tree.BlockStatement, javalang.tree.Creator, javalang.tree.SwitchStatementCase)):
                        called_methods.update(self.construct_called_methods(class_name, graph_dict,
                                                                        called_methods, self.flatten_attributes(statement_attributes)))
        return called_methods

		