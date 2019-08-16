--
-- Name: keyfile_temp_nofastq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE keyfile_temp_nofastq FROM PUBLIC;
REVOKE ALL ON TABLE keyfile_temp_nofastq FROM agrbrdf;
GRANT ALL ON TABLE keyfile_temp_nofastq TO agrbrdf;
GRANT SELECT ON TABLE keyfile_temp_nofastq TO gbs;


