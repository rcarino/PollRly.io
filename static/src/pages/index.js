import React from 'react';
import PropTypes from 'prop-types';
import Typography from 'material-ui/Typography';
import {withStyles} from 'material-ui/styles';
import withRoot from '../withRoot';
import Button from 'material-ui/Button';
import Card, {CardActions, CardContent, CardHeader} from 'material-ui/Card';
import axios from 'axios';
import Radio, {RadioGroup} from 'material-ui/Radio';
import {FormControlLabel} from 'material-ui/Form';
import _ from 'lodash';

const styles = theme => ({
    root: {
        paddingTop: theme.spacing.unit * 20,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
    },

    card: {
        maxWidth: 800
    },

    submit: {
        marginLeft: 'auto'
    }
});

class Index extends React.Component {

    state = {};

    async componentDidMount() {
        const resp = (await axios.get('api/questions/random')).data; // TODO: handle network error
        this.setState({'question': resp});

    }

    handlePick = (event, pickedOption) => this.setState({'pickedOption': Number(pickedOption)});

    async handleSubmit() {
        await axios.post(`api/questions/${this.state.question.id}/votes/${this.state.pickedOption}`);
        window.location.href = `votes.html?qid=${this.state.question.id}`
    }

    render() {
        const {classes} = this.props;

        return (
            <div className={classes.root}>
                <Typography variant="display1" gutterBottom>
                    PollRly.io
                </Typography>

                <Card className={classes.card}>
                    <CardHeader title={_.get(this.state, 'question.question')}/>
                    <CardContent>
                        <RadioGroup
                            onChange={this.handlePick}
                            value={this.state.pickedOption}>
                            {_.get(this.state, 'question.options', [])
                                .map((v, i) => (<FormControlLabel value={i} control={<Radio/>} label={v}/>))}
                        </RadioGroup>
                        <CardActions>
                            <Button
                                className={classes.submit}
                                variant="raised"
                                color="primary"
                                disabled={this.state.pickedOption === undefined}
                                onClick={this.handleSubmit.bind(this)}>
                                Vote
                            </Button>
                        </CardActions>
                    </CardContent>
                </Card>
            </div>
        );
    }
}

Index.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withRoot(withStyles(styles)(Index));
