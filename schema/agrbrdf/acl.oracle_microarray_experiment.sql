--
-- Name: oracle_microarray_experiment; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oracle_microarray_experiment FROM PUBLIC;
REVOKE ALL ON TABLE oracle_microarray_experiment FROM agrbrdf;
GRANT ALL ON TABLE oracle_microarray_experiment TO agrbrdf;
GRANT SELECT ON TABLE oracle_microarray_experiment TO gbs;


