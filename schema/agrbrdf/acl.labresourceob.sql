--
-- Name: labresourceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourceob FROM PUBLIC;
REVOKE ALL ON TABLE labresourceob FROM agrbrdf;
GRANT ALL ON TABLE labresourceob TO agrbrdf;
GRANT SELECT ON TABLE labresourceob TO gbs;


