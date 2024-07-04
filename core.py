from paths import *
from clients import *
from accuracy import *
from aggregation import *
from labelflip import *
from fileupload import *
from malremove import *
from imutils import paths
import pickle
import h5py
from tensorflow.python.keras.models import Model
import subprocess
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import gradient_descent_v2
from tensorflow.python.keras import backend as K
import threading
import time

from dashboard import *


def pre_run():
    image_paths = list(paths.list_images(img_path))
    random.shuffle(image_paths)
    num_images = int(len(image_paths) * 0.1)
    image_list, label_list = load(image_paths[:num_images],verbose=10000)

    lb = LabelBinarizer()
    label_list = lb.fit_transform(label_list)

    #split data fro trainig and testing
    X_train, X_test, y_train, y_test = train_test_split(image_list, label_list, test_size=0.1, random_state=42)

    client = create_clients(X_train, y_train, num_clients=10, initial='clients')

    #batch the training data for each clients
    #clients_batched = dict()

    for(client_names, data) in client.items():
        clients_batched[client_names] = batch_data(data)

    #batch the test data
    test_batched = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(len(y_test))

    #label count of client
    # label_count_of_clients('clients_1')
    #label_count_of_clients('clients_2')
    #label_count_of_clients('clients_3')
    #label_count_of_clients('clients_4')
    #label_count_of_clients('clients_5')
    
    return test_batched

#filp 1 into 7
# label_flip('clients_1', 1, 7)
# label_flip('clients_2', 1, 7)
# label_flip('clients_3', 1, 7)
# label_flip('clients_4', 1, 7)
# label_flip('clients_5', 1, 7)
# label_flip('clients_6', 1, 7)
# label_flip('clients_7', 1, 7)
# label_flip('clients_8', 1, 7)
# label_flip('clients_9', 1, 7)
# label_flip('clients_10', 1, 7)

def run_label_flip(number):
    # label_count_of_clients('clients_1')
    test_batched = pre_run()
    # label_count_of_clients('clients_1')
    for i in range(1,number+1):
        if number == 0:break
        client = 'clients_'+str(i)
        label_flip(client,1,7)
    # label_count_of_clients('clients_1')
    return post_run(test_batched)
        

def post_run(test_batched):
        
    #compiling the model

    #for SGD optimizer
    learning_rate = 0.1
    iterations = 2
    epsilon = 1.0  # Initial privacy budget
    alpha = learning_rate / iterations  # Learning rate for Foolsgold
    max_noise = 1.0  # Maximum noise magnitude

    #no.of communicatio rounds

    loss = 'categorical_crossentropy'
    metrics= ['accuracy']
    optimizer = gradient_descent_v2.SGD(learning_rate=alpha, momentum=0.9)


    tp_div_support_dict = np.zeros((iterations, 10))

    #Initialize the global model

    smlp_global = SimpleMLP()
    global_model = smlp_global.build(784,10)
    timeout_duration = 300
    datarequest = True
    
    send_acc = []

    #Load the model weights using h5py
    # loaded_model_weights = []
    # with h5py.File('./web3-storage-quickstart/global_model/global_model_weights.h5', 'r') as hf:
    #     for i in range(len(hf.keys())):
    #         loaded_model_weights.append(hf[f'layer_{i}'][:])
            
    # global_model.set_weights(loaded_model_weights)

    # Function to run get_cid_of_data with a timeout


    for comm_round in range(iterations):

        #get the global model's weights (In each communication round, the current global model weights are retrieved with)
        global_weights = global_model.get_weights()

        scaled_local_weight_list = list()

        #randomize client data using keys to access each client batch data in the clients_batched dictionary
        client_names = list(clients_batched.keys())
        random.shuffle(client_names)

        index_ID = 1  
        #loop through each client and create new local model
        for client in client_names:
                smlp_local = SimpleMLP()
                local_model = smlp_local.build(784,10)

                local_model.compile( loss = loss,
                                    optimizer= optimizer,
                                    metrics= metrics)

                local_model.set_weights(global_weights)

                clients_train = clients_batched[client]
                for batchdata, labeldata in clients_train:
                    train_x = np.asarray(batchdata)
                    train_y = np.asarray(labeldata)
                    local_model.fit(train_x, train_y, epochs=5, verbose=0)

                # for(X_test, Y_test) in test_batched:
                #       local_acc, local_loss = test_model(X_test, Y_test, local_model, comm_round, 'localModel', client)
                #scale the model weights and add to list
                scaling_factor = weight_scalling_factor(clients_batched, client)
                scaled_weights = scale_model_weights(local_model.get_weights(), scaling_factor)
                scaled_local_weight_list.append(scaled_weights)
                #scaled_local_weight_list.append((client, scaled_weights)) # add client name to the list

                weight_vector = np.concatenate([matrix.flatten() for matrix in scaled_weights])
                weight_vector_list = weight_vector.tolist()

                # Convert the variable to a file
                file_path = "./web3-storage-quickstart/clients_model/{}.txt".format(client)
                file_content = str(weight_vector_list)  # Convert the variable to a string if necessary
                with open(file_path, "w") as file:
                    file.write(file_content)

                #content_ID = client_model_upload(client)
                #add_block(index_ID,content_ID,client)
                #index_ID = index_ID + 1

                
                #clear session to free memory after each communication round
                tf.keras.backend.clear_session()
                
        # content_ID = model_upload('clients_model')
        # off_chain_request(content_ID)
        # while(run_get_cid_with_timeout()):
        #     off_chain_request(content_ID)
        
        #cid = get_cid_of_data_ar1()
        
        #remove malicious clients
        #verified_scaled_local_weight_list = mal_remove(malicious_client, scaled_local_weight_list)

        #to get the average over all the local model, we simply take the sum of the scaled weights
        average_weights = sum_scaled_weights(scaled_local_weight_list)
        #average_weights = get_aggregation_data(cid)
        #average_weights = get_aggregation_data('bafybeibijee3jftyczhutmotrlimksmoxzlpwwglmlvtqeo6jy3jypflv4')
        #   average_weights = median_scaled_weights(scaled_local_weight_list)
        #FedAverage_weights = sum_scaled_weights(verified_scaled_local_weight_list, len(client_names))

        #update global model
        global_model.set_weights(average_weights)
        #global_model.set_weights(FedAverage_weights)

        
        #Save the model weights using h5py
        #   model_weights = global_model.get_weights()
        #   with h5py.File('./web3-storage-quickstart/global_model/global_model_weights.h5', 'w') as hf:
        #       for i, layer_weights in enumerate(model_weights):
        #           hf.create_dataset(f'layer_{i}', data=layer_weights)

        #   content_ID = model_upload('global_model')
        
        #   #Load the model weights using h5py
        #   global_models = smlp_global.build(784,10)
        #   loaded_model_weights = []
        #   with h5py.File('./web3-storage-quickstart/global_model/global_model_weights.h5', 'r') as hf:
        #       for i in range(len(hf.keys())):
        #           loaded_model_weights.append(hf[f'layer_{i}'][:])

        #   #Set the loaded weights to the model
        #   global_models.set_weights(loaded_model_weights)


        #test global model and print out metrics after each communications round
        for(X_test, y_test) in test_batched:
            global_acc, global_loss = test_model(X_test, y_test, global_model, comm_round, 'globalModel','')
            send_acc.append(global_acc)

        #get accuracy scores
        tp_div_support_dict = classes_acc_testss(X_test, y_test, global_model, comm_round, tp_div_support_dict)

    file_path = "./web3-storage-quickstart/graph_plot/0meanAccu10.txt"
    file_content = str(tp_div_support_dict)  # Convert the variable to a string if necessary
    with open(file_path, "w") as file:
        file.write(file_content)

    image1 = confusion_matrix_acc(global_model,X_test,y_test)

    # plot predict scores for each label
    image2 = predic_acc(tp_div_support_dict,iterations)
    
    response_data = {
        "image1":image1,
        "image2":image2,
        "acc": send_acc
    }
    
    return response_data

#validate the filpped data
# label_count_of_clients('clients_1')
#label_count_of_clients('clients_2')
#label_count_of_clients('clients_3')
#label_count_of_clients('clients_4')
#label_count_of_clients('clients_5')

#defining the neural network
class SimpleMLP:
    @staticmethod
    def build(shape, classes):
        model = Sequential()
        model.add(Dense(50, input_shape=(shape,)))
        model.add(Activation("relu"))
        #model.add(Dense(200))
        #model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model
        # model.add(Dense(1024, input_shape=(shape,)))
        # model.add(Activation("relu"))
        # model.add(Dense(512))
        # model.add(Activation("relu"))
        # model.add(Dense(128))
        # model.add(Activation("relu"))
        # model.add(Dense(classes))
        # model.add(Activation("softmax"))
        # return model





def run_get_cid_with_timeout(timeout_duration):
    global cid
    cid = None
    def target():
        global cid
        cid = get_cid_of_data_ar1()
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout_duration)

    if thread.is_alive():
        print("Timeout occurred for get_cid_of_data. Running off_chain_request.")
        return True

    return False
    