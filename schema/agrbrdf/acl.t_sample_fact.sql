--
-- Name: t_sample_fact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE t_sample_fact FROM PUBLIC;
REVOKE ALL ON TABLE t_sample_fact FROM agrbrdf;
GRANT ALL ON TABLE t_sample_fact TO agrbrdf;
GRANT SELECT ON TABLE t_sample_fact TO gbs;


