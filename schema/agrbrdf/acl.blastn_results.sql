--
-- Name: blastn_results; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE blastn_results FROM PUBLIC;
REVOKE ALL ON TABLE blastn_results FROM agrbrdf;
GRANT ALL ON TABLE blastn_results TO agrbrdf;
GRANT SELECT ON TABLE blastn_results TO gbs;


