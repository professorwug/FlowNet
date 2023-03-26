# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04 Training Machinery/04a Scheduling.ipynb (unless otherwise specified).

__all__ = ['general_scheduler', 'specific_scheduler']

# Cell
def general_scheduler(Dictionary loss_weights, char loss_name, int epoch, int total_epochs, int c=1, char function_type="sigmoid"):
    '''
    Inputs
    loss_weights: Dictionary of loss names and their weights
    loss_name: the loss in the loss_weights to be scheduled
    epoch: current epoch
    total_epochs: total number of epochs that will be run
    c: scaler multiple for sigmoid, or slope for linear
    function_type: type of function for the scheduler, can be
        "sigmoid": sigmoid 1 / (1 + np.exp(c(-epoch+np.floor(total_epochs/2))))
        "off": 1 - "sigmoid"
        "linear": linear with slope c
        "loglinear": log linear with weight c

    Return
    loss_weights dictionary with updated weight for the specified loss function at the current epoch
    '''
    if function_type == "sigmoid":
        new_weight = 1 / (1 + np.exp(-epoch+np.floor(total_epochs/2)))
    elif function_type == "off"
        new_weight = 1 - (1 / (1 + np.exp(-epoch+np.floor(total_epochs/2))))
    loss_weights[loss_name] = new_weight
    elif function_type == "linear"
        new_weight = c*epoch
    elif function_type == "loglinear"
        new_weight = np.exp(c*epoch)
    return loss_weights


# Cell
def specific_scheduler(Dictionary loss_weights, int epoch):
    loss_weights = sigmoid_scheduler(loss_weights, loss_name="smoothness", epoch, total_epochs=10, c=1, function_type="sigmoid")
    # change parameters manually, however you'd like:
    # loss_weights = sigmoid_scheduler(loss_weights, loss_name="flow neighbor loss", epoch, total_epochs=20, c=5, function_type="off")
    # loss_weights = sigmoid_scheduler(loss_weights, loss_name="distance regularization", epoch, total_epochs=20, c=1, function_type="off")
    return loss_weights